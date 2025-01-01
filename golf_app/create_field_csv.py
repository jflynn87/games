import csv
from golf_app.models import Tournament, Field
import boto3
from io import StringIO
import os


class FieldCSV(object):
    def __init__(self, tournament):
        self.t = tournament
        self.all_tournaments_presort = Tournament.objects.filter(season__season__in = [self.t.season.season, self.t.season.season -1]).exclude(pga_tournament_num__in=['468', '500', '999']).exclude(current=True)
        self.all_tournaments = sorted(self.all_tournaments_presort, key=lambda x: x.pk, reverse=True)
        self.field = Field.objects.filter(tournament=self.t)
        self.static_header_fields = [
            'ESPN ID', 'Golfer','Group ID', 'currentWGR', 'sow_WGR', 'soy_WGR', 'prior year finish',
            'handicap', 'FedEx Rank', 'FedEx Points', 'Season Played', 'Season Won', 'Season 2-10',
             'Season 11-29', 'Season 30 - 49', 'Season > 50', 'Season Cut'
             ]

        self.variable_header_fields = []
        for t in self.all_tournaments:
            self.variable_header_fields.append(t.name)

        self.s3_bucket = 'jflynn87-games-files'  # Configure your bucket name
        self.s3_key = self.t.s3_csv_key()  # Define your S3 path/key

   
    def create_file(self):
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)
        writer.writerow([h for h in self.static_header_fields + self.variable_header_fields])

        data = []
        for f in self.field:
            data.append(self.format_row(f))
        writer.writerows(data)

        try:
            s3_client = boto3.client('s3',
                aws_access_key_id=os.environ.get('AWS_GAMES_KEY'),
                aws_secret_access_key=os.environ.get('AWS_GAMES_SECRET'),
                region_name='us-west-2'
            )
            
            # Upload the file
            s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=self.s3_key,
                Body=csv_buffer.getvalue(),
                ContentType='text/csv'
            )
            
            return self.s3_key
            
        except Exception as e:
            print(f"Error uploading to S3: {str(e)}")
            return f"error {e}"

    def format_row(self, f):
        if f.season_stats:
            s = f.season_stats.get('stats', {'no_stats': ''})
        else:
            s = {'no_stats': ''}
        
        row = [f.golfer.espn_number, f.playerName, f.group.number, f.currentWGR, f.sow_WGR, f.soy_WGR, f.prior_year, f.handi, 
               s.get('fed_ex_rank', ''), s.get('fed_ex_points', ''), s.get('played', ''), s.get('won', ''), s.get('top10', ''), s.get('bet11_29', ''), 
               s.get('bet30_49', ''), s.get('over50', ''), s.get('cuts', ''), 
               ]
        
        season_results = f.golfer.get_season_results(t_list=self.all_tournaments)

        for t in self.all_tournaments:
            row.append(season_results.get(t.pk).get('rank', 'n/a'))
        return row
    
