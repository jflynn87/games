from re import split
from unidecode import unidecode as decode
from datetime import datetime
import os
from decimal import Decimal



def format_score(score):
    '''takes in a sting and returns a string formatted for the right display or calc'''
    if score == None:
        return "not started"
    if score == 0:
        return 'E'
    elif score > 0:
        return ('+' + str(score))
    else:
        return score

def score_as_int(score, t=None, sd=None):
    '''takes a string or int and optional tournament object and score dict.  returns an int.  Returns 999 if any issues'''
    if score is int:
        return score
    elif score == "E":
        return 0
    elif len(score) > 1 and score[0] in ['+', '-']:
        return score
    elif t and score in t.not_playing_list():
        try:
            return int(sd.get('info').get('cut_num'))
        except Exception as e:
            print ('score as int sd lookup exception', t, sd, e)
            return 999
    else:
        print ('uitils score as int cant resolve ', score)
        return 999



def formatRank(rank, tournament=None):
    from golf_app.models import Tournament
    '''takes in a sting and optional tournament object, returns an int'''

    try:
        t = Tournament.objects.get(current=True)
    except Exception as e:
        t = Tournament.objects.all().order_by('-pk').first()
    
    if type(rank) is int:
        return rank
    elif rank in  ['', '--', '-', None]:
        return t.saved_cut_num
        #return 999 - (len(t.not_playing_list()) +1)
    elif rank in t.not_playing_list():
        return 999 - t.not_playing_list().index(rank)
    elif rank[0] != 'T':
       return int(rank)
    elif rank[0] == 'T':
       return int(rank[1:])
    #elif rank == "E":
    #    return 0
    else:
       return rank

def format_name(name):
    '''take a name string and match pga conventions '''
    if len(name.split(' ')) == 2:
        return name
    else:
        #print (name.split(' '))
        return (name.strip(', Jr.').strip(',Jr ').strip('(a)').strip(',').strip('Jr.').strip('.'))


def fix_name(player, owgr_rankings, log=None):
    '''takes a string and a dict and returns a tuple'''

    log = False
    if log:
        print ('FIX: ', player, len(owgr_rankings))
    if owgr_rankings.get(player.replace('.', '').replace('-', '').replace(' ', '')) != None:
        return (player, owgr_rankings.get(player.replace('.', '').replace('-', '')))

    if owgr_rankings.get(decode(player)):
        if log:
            print ('unidecoded name dict match: ', player, owgr_rankings.get(decode(player)))
        return (player, owgr_rankings.get(decode(player)))

    lower = [v for k,v in owgr_rankings.items() if player.lower() == k.lower()]
    if len(lower) > 0:
        return (player, lower[0])

    replace_list = ['-', "'", " "]
    for char in replace_list:
        strip  = [v for k,v in owgr_rankings.items() if player.replace(char, '').lower() == k.replace(char, '').lower()]
        if len(strip) > 0:
            return (player, strip[0])

    if log:
        print (['Checking name in db', player])

    from golf_app.models import Name
    #need to import here to avoid cicular import error
    
    if Name.objects.filter(PGA_name=player).exists():
        if log:
            print ('player mathc')
        name = Name.objects.get(PGA_name=player)
        if owgr_rankings.get(name.OWGR_name):
            if log:
                print ('returning based on name table lookup: ', player, owgr_rankings.get(name.OWGR_name))
            return (player, owgr_rankings.get(name.OWGR_name))

    last = player.split(' ')
    
    if last[len(last)-1] in ['Jr', 'Jr.', '(a)'] or last[len(last)-1].isupper():
        last_name = last[len(player.split(' ')) - 2]
    else:
        last_name = last[len(last)-1]
    
    possible_matches = {k:v for k,v in owgr_rankings.items() if decode(last_name.strip(',')) in decode(k)}
    
    if log:
        print ('player: ', player)
    #print ('possible name mathces: ', player, possible_matches)

    pga_name = player.replace(' (a)', '').replace(',', '').replace('.', '').replace('-', '').split(' ')

    #for k, v in owgr_rankings.items():
    for k, v in possible_matches.items():
        owgr_name = k.replace(',', '').split(' ')
        if log:
            print ('looping thru possible: ', pga_name, owgr_name)
        if owgr_name == pga_name:
            if log:
                print ('names equal after strip spec chars', player, owgr_name)
            return player, v

        if len(owgr_name) == 3 and len(pga_name) == 3 and decode(owgr_name[0]) == decode(pga_name[0]) \
            and decode(owgr_name[2].replace('.', '')) == decode(pga_name[2].replace('.', '')) and owgr_name[1][0] == pga_name[1][0]:
                if log:
                    print ('last name, first name match, middle first intial match', player, owgr_name)
                return k, v
        elif decode(owgr_name[len(owgr_name)-2]) == decode(pga_name[len(pga_name)-1]) \
            and k.split(' ')[0] == player.split(' ')[0]:
            if log:
                print ('XXXXX fix this for dru love')
                print ('last name, first initial match, cut owgr suffix', k, v, player, owgr_name)
            return k, v
        elif decode(owgr_name[0].replace('-', '')) == decode(pga_name[len(pga_name)-1].replace('-', '')) \
            and decode(owgr_name[len(owgr_name)-1].replace('-', '')) == decode(pga_name[0].replace('-', '')):
            if log:
                print ('names reversed', player, owgr_name)
            return k, v
        elif decode(owgr_name[len(owgr_name)-1]) == decode(pga_name[len(pga_name)-1]) \
           and k[0:2] == player[0:2]:
            if log:
                print ('last name, first two letter match', player, owgr_name)
            return k, v

    if log or os.environ.get("DEBUG") != "True":
        print ('fix names didnt find match', player)
    return None, [9999, 9999, 9999]


def check_t_names(espn_t, t):
    '''Takes a string and a tournament object and returns a bool'''
    if espn_t == t.name:
        return True
    
    if espn_t[:3] == "WGC":
        espn_t = "world golf championships" + espn_t[3:]
        print ('correcting WGC', espn_t, t)

    if '@' in espn_t:
        print ('stripping @ from espn t name', espn_t)
        espn_t = espn_t.split('@')[0].strip()

    #print ('checking t name match espn: ', espn_t, ' pga: ', t.name)
    espn_name = espn_t.lower().split(' ')
    pga_name = t.name.lower().split(' ')
    #print ('espn name: ', espn_name)
    #print ('pga name: ', pga_name)
    matches = len([x for x in pga_name if x in espn_name])
    #print ('matches: ', matches == len(espn_name) -1, espn_name[1])
    if len(pga_name) < 4 and espn_name == pga_name:
        return True
    #added below for masters, could be better
    elif espn_name[0] == str(t.season.season) and matches == len(espn_name) -1:
        print ('returning true match by removing year from espn')
        return True
    elif len(pga_name) > 3 and matches > len(pga_name)/2:
        return True
    else:
        #return True
        return False

def reverse_names(name):
    #print (name, len(name.rstrip(' ').split(' ')), name.rstrip(' ').split(' '))
    work_list = name.rstrip(' ').split(' ')
    #print (work_list)
    names = list(filter(None, work_list))
    print(names)
    ret_val = ''
    for n in names:
        if len(ret_val) > 0:
            ret_val += ' '
        ret_val += n
    print (ret_val)
    return ret_val

    #if len(names) == 2:
    #    return names[0] + ' ' + names[1]
    #elif len(names) == 3:
    #    return names[0] + ' ' + names[1] + ' ' + names[2]
    #else:
    #    print ('unexpected name: ', name)
    #    return names[len(names)-1] + ' ' + names[0] 


def save_access_log(request, screen):
    '''takes a request and a string saves an object and returns nothing'''
    from golf_app.models import AccessLog, Tournament
    try:
        if request.user.is_authenticated:
            log, created = AccessLog.objects.get_or_create(tournament=Tournament.objects.get(current=True), user=request.user, page=screen, device_type=request.user_agent)
            #log.user = request.user
            #log.page = screen
            log.views += 1
            log.save()
    except Exception as e:
        print ('save access log issue: ', e)
    return


def post_cut_wd_count(t, sd=None, api_data=None):
    '''takes a tournament and optional score dict or espn api field data(must have 1 of them), returns an int'''
    if not sd and not api_data:
        raise Exception('utils post cut WD requires a score dict or api data')
    
    if sd:
        return len([v for k,v in sd.items() if k!= 'info' and v.get('total_score') in t.not_playing_list() and \
                    v.get('r3') != '--'])

    if api_data:
        l = t.not_playing_list()
        l.remove('CUT')
        return len([x.get('athlete').get('id') for x in api_data if x.get('status').get('type').get('id') == '3' \
                and x.get('status').get('type').get('shortDetail') in l and int(x.get('status').get('period')) > t.saved_cut_round]) 


def name_first_last(n):
    '''
    Converts "lastname, firstname" to "firstname lastname"
    Preserves spaces in both first and last names
    Examples:
        "Smith, John" -> "John Smith"
        "de la Cruz, Maria" -> "Maria de la Cruz"
        "Kim, Ye Jin" -> "Ye Jin Kim"
        "Lee, Sung Hee" -> "Sung Hee Lee"
    '''
    if not n or ',' not in n:
        return n
        
    # Split on first comma only
    parts = n.split(',', 1)
    last_name = parts[0].strip()
    first_name = parts[1].strip()
    
    return f"{first_name} {last_name}"

def convert_floats_to_decimal(data):
    """Convert all float values in a dict/list structure to Decimal"""
    if isinstance(data, dict):
        return {k: convert_floats_to_decimal(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_floats_to_decimal(v) for v in data]
    elif isinstance(data, float):
        return Decimal(str(data))  # Convert to string first for better precision
    return data

# #try this later, Q suggestion for more robust process
# def normalize_name(name: str, remove_suffixes: bool = True) -> str:
#     """
#     Normalizes a player name by applying consistent formatting rules.
    
#     Args:
#         name: The player name to normalize
#         remove_suffixes: Whether to remove common suffixes like Jr., III, etc.
    
#     Returns:
#         Normalized name string
        
#     Examples:
#         >>> normalize_name("TIGER WOODS")
#         "Tiger Woods"
#         >>> normalize_name("de la Cruz, José-María")
#         "Jose-Maria de la Cruz"
#         >>> normalize_name("JOHNSON, Dustin (Jr.)")
#         "Dustin Johnson"
#         >>> normalize_name("JOHNSON, Dustin (Jr.)", remove_suffixes=False)
#         "Dustin Johnson Jr."
#     """
#     if not name:
#         return ""

#     # Common suffixes to handle
#     SUFFIXES = {
#         'JR', 'JR.', 'SR', 'SR.', 'II', 'III', 'IV', 
#         '(A)', '(A.)', '(AM)', '(AM.)', '(AMATEUR)'
#     }

#     # Special case prefixes that should remain lowercase
#     NAME_PREFIXES = {'de', 'van', 'von', 'del', 'della', 'la', 'das', 'dos'}

#     def clean_string(text: str) -> str:
#         """Remove extra whitespace and standardize separators"""
#         # Replace multiple spaces with single space
#         text = ' '.join(text.split())
#         # Remove parentheses
#         text = text.replace('(', '').replace(')', '')
#         return text.strip()

#     def handle_suffix(name_parts: list) -> tuple[list, str]:
#         """Separate name and suffix"""
#         suffix = ''
#         clean_parts = []
        
#         for part in name_parts:
#             part = part.strip('(),')
#             if part.upper() in SUFFIXES:
#                 suffix = part
#             else:
#                 clean_parts.append(part)
                
#         return clean_parts, suffix

#     # First, decode any special characters
#     name = decode(name)
    
#     # Handle "lastname, firstname" format
#     if ',' in name:
#         last_name, first_name = name.split(',', 1)
#         name = f"{first_name.strip()} {last_name.strip()}"
    
#     # Clean and split the name
#     name = clean_string(name)
#     parts = name.split()
    
#     # Handle suffixes
#     name_parts, suffix = handle_suffix(parts)
    
#     # Properly capitalize each part
#     normalized_parts = []
#     for part in name_parts:
#         # Handle hyphenated names
#         if '-' in part:
#             normalized_parts.append('-'.join(p.capitalize() for p in part.split('-')))
#         # Handle prefixes
#         elif part.lower() in NAME_PREFIXES:
#             normalized_parts.append(part.lower())
#         # Normal capitalization
#         else:
#             normalized_parts.append(part.capitalize())
    
#     # Reconstruct the name
#     normalized_name = ' '.join(normalized_parts)
    
#     # Add suffix if requested
#     if not remove_suffixes and suffix:
#         normalized_name = f"{normalized_name} {suffix.title()}"
    
#     return normalized_name


# def fix_name(player, d, log=None):
#     """takes a string and a dict and returns a tuple"""
    
#     # Normalize both the player name and all OWGR names for comparison
#     normalized_player = normalize_name(player)
#     normalized_rankings = {
#         normalize_name(k): v 
#         for k, v in d.items()
#     }
    
#     # Direct match with normalized names
#     if normalized_player in normalized_rankings:
#         return (player, normalized_rankings[normalized_player])
    
    # Continue with other matching strategies...
