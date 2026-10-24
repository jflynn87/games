import os
import io
from fb_app.models import Week, Player, Picks, Teams, MikeScore, WeekScore, League
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from fb_app import validate_picks
from docx.api import Document


class SheetLoader:

    S3_BUCKET = 'jflynn87-games-files'
    S3_PREFIX = 'fools'

    def __init__(self, file, num_players, override_week=None, etag=None):
        self.etag = etag          
        
        self.file = file
        self.num_players = num_players
        self.app_week = override_week or Week.objects.get(current=True)
        self.season = self.app_week.season_model.season
        self.week = self.app_week.week
        self.mike_score_week = (
            self.app_week if self.week == 1
            else Week.objects.get(season_model__current=True, week=self.week - 1)
        )
        self.document = None
        self.sheet_data = None

    def load(self):
        self._open_document()
        self.sheet_data = self._parse_sheet()
        valid, errors = self._validate_sheet()
        if not valid:
            raise ValueError(f"Sheet validation failed: {errors}")
        self._delete_existing_picks()
        resp = self._save_picks()
        return resp

    # --- Document loading ---

    def _open_document(self):
        if self.etag:
            print(f"ETag provided: {self.etag}, skipping local file check.")
            self._open_from_s3()
            if self.document is None:
                raise FileNotFoundError(
                    f"Could not find football sheet for season {self.season} week {self.week} in S3 with ETag {self.etag}"
                )
            return
        for candidate in self._local_candidates():
            if os.path.exists(candidate):
                print(f"Opening local file: {candidate}")
                self.document = Document(candidate)
                return
        print("No document found locally, checking S3...")
        self._open_from_s3()
        if self.document is None:
            raise FileNotFoundError(
                f"Could not find football sheet for season {self.season} week {self.week} locally or in S3"
            )

    def _local_candidates(self):
        s, w = self.season, self.week
        return [
            self.file,
            f"Football sheet {s}.docx",
            f"football sheet {s}.docx",
            f"Football Sheet {s} Week {w}.docx",
            f"football Sheet {s} Week {w}.docx",
            f"Football sheet {s} Week {w}.docx",
            f"football sheet {s} Week {w}.docx",
        ]

    def _s3_candidates(self):
        s, w = self.season, self.week
        return [
            f"Football Sheet {s} Week {w}.docx",
            f"football Sheet {s} Week {w}.docx",
            f"Football sheet {s} Week {w}.docx",
            f"football sheet {s} Week {w}.docx",
            f"Football sheet {s}.docx",
            f"football sheet {s}.docx",
        ]

    def _open_from_s3(self):
        import boto3
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_GAMES_KEY'),
            aws_secret_access_key=os.environ.get('AWS_GAMES_SECRET'),
        )

        if self.etag:
            print(f"Searching S3 for file with ETag: {self.etag}")
            response = s3.list_objects_v2(Bucket=self.S3_BUCKET, Prefix=self.S3_PREFIX)
            if 'Contents' not in response:
                return
            for obj in response['Contents']:
                if obj.get('ETag') == self.etag:
                    print(f"Found matching S3 object: {obj['Key']}")
                    objresponse = s3.get_object(Bucket=self.S3_BUCKET, Key=obj['Key'])
                    if objresponse.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                        self.document = Document(io.BytesIO(objresponse['Body'].read()))
                        print(f"Opened from S3: {obj['Key']}")
                        return
            print("No matching S3 object found with the provided ETag.")
            return
        
        response = s3.list_objects_v2(Bucket=self.S3_BUCKET, Prefix=self.S3_PREFIX)
        if 'Contents' not in response:
            return

        keys = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.docx')]
        match = self._find_best_s3_key(keys)
        if match is None:
            return

        print(f"Trying S3: s3://{self.S3_BUCKET}/{match}")
        obj = s3.get_object(Bucket=self.S3_BUCKET, Key=match)
        self.document = Document(io.BytesIO(obj['Body'].read()))
        print(f"Opened from S3: {match}")

    def _find_best_s3_key(self, keys):
        s, w = str(self.season), str(self.week)
        # score each key by how many expected tokens it contains
        tokens = ['football', 'sheet', s, w]
        def score(key):
            lower = key.lower()
            return sum(t.lower() in lower for t in tokens)
        
        candidates = [k for k in keys if score(k) >= 3]  # must match at least season + "football sheet"
        return max(candidates, key=score, default=None)

    # --- Parsing ---

    def _parse_sheet(self):
        table = self.document.tables[0]
        rows = table.rows

        week_str = rows[0].cells[0].text.strip()
        print(f"Sheet Week: {week_str}")
        players = [c.text.strip() for c in rows[0].cells[1:] if c.text.strip()]

        data = {p: {'picks': [], 'score': None} for p in players}

        pick_rows = []
        for row in rows[1:]:
            cells = [c.text.strip() for c in row.cells]
            if any(cells[1:len(players) + 1]):
                pick_rows.append(cells)

        has_scores = all(
            v.isdigit() and int(v) > 16
            for v in pick_rows[-1][1:len(players) + 1] if v
        )
        score_row = pick_rows.pop() if has_scores else None

        for i, player in enumerate(players):
            data[player]['picks'] = [
                {'pick_num': row[0], 'team': row[i + 1]}
                for row in pick_rows if i + 1 < len(row) and row[i + 1]
            ]
            if score_row:
                data[player]['score'] = score_row[i + 1] if i + 1 < len(score_row) else None

        return {'week': week_str, 'has_scores': has_scores, 'players': data}

    # --- Validation ---

    def _validate_sheet(self):
        errors = []
        week_str = self.sheet_data['week']

        if str(self.week) != week_str:
            errors.append(f"Sheet week {week_str} doesn't match DB week {self.week}")
            return False, errors

        expected_picks = self.app_week.game_cnt
        has_scores = self.week > 1

        for player, data in self.sheet_data['players'].items():
            valid_picks = [p for p in data['picks'] if p['pick_num'].isdigit()]
            if len(valid_picks) != expected_picks:
                errors.append(f"{player}: expected {expected_picks} picks, found {len(valid_picks)}")
            if has_scores and data['score'] is None:
                errors.append(f"{player}: missing season score")

        if errors:
            for e in errors:
                print(f"VALIDATION ERROR: {e}")
            return False, errors

        print("Sheet validated OK")
        return True, []

    # --- DB writes ---

    def _delete_existing_picks(self):
        league = League.objects.get(league="Football Fools")
        if Picks.objects.filter(week=self.app_week, player__league=league).exists():
            Picks.objects.filter(week=self.app_week, player__league=league).delete()
            MikeScore.objects.filter(week=self.app_week, player__league=league).delete()
            print("Deleted existing picks")

    def _save_picks(self):
        l = []
        for player_name, data in self.sheet_data['players'].items():
            user = User.objects.get(username=player_name.replace(' ', ''))
            player = Player.objects.get(name=user)
            score_msg = self._save_score(player, data)
            picks_msg = self._save_player_picks(player, data['picks'])
            l.append({'player_name': player_name, 'score_msg': score_msg, 'picks_msg': picks_msg})
        return l
    def _save_score(self, player, data):
        if not self.sheet_data['has_scores']:
            return
        scores = MikeScore()
        scores.week = self.mike_score_week
        scores.player = player
        scores.total = data['score']
        scores.save()

        my_total = sum(
            s.score for s in WeekScore.objects.filter(
                week__lte=self.mike_score_week,
                player=player,
                week__season_model__current=True,
            )
        )
        if int(my_total) != int(scores.total):
            msg = f"**** Score mismatch: {player} calc={my_total} sheet={scores.total}"
            print(msg)
        else:
            msg = f"Score good: {player} {my_total}"
            print(msg)
        
        return msg

    def _save_player_picks(self, player, picks):
        pick_list = []
        for pick in picks:
            if not pick['pick_num'].isdigit():
                continue
            pick_team = self._lookup_team(pick['team'], player)
            if pick_team is None:
                continue
            sheet_pick = Picks()
            sheet_pick.player = player
            sheet_pick.week = self.app_week
            sheet_pick.pick_num = pick['pick_num']
            sheet_pick.team = pick_team
            sheet_pick.save()
            pick_list.append(str(pick_team))

        picks_check = validate_picks.validate(pick_list, self.app_week)
        if not picks_check[0]:
            msg = f"**** Picks invalid: {player} - {picks_check[1]}"
            print(msg)
        else:
            msg = f"Picks valid: {player}"
            print(msg)
        
        return msg

    def _lookup_team(self, abbr, player):
        try:
            return Teams.objects.get(mike_abbr=abbr)
        except ObjectDoesNotExist:
            pass
        try:
            return Teams.objects.get(typo_name=abbr)
        except ObjectDoesNotExist:
            pass
        try:
            return Teams.objects.get(typo_name1=abbr)
        except ObjectDoesNotExist:
            print(f"Team not found: {abbr} for {player}")
            return None


#SheetLoader('Football sheet 2026.docx', 27).load()
