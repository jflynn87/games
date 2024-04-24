from re import split
from unidecode import unidecode as decode
from datetime import datetime
import os


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
    '''takes a string and a dict and returns a dict?'''

    from golf_app.models import Name
    #need to import here to avoid cicular import error
    log = True
    print ('FIX: ', player)
    if owgr_rankings.get(player.replace('.', '').replace('-', '')) != None:
        #print ('returning match', owgr_rankings.get(player.replace('.', '').replace('-', '')))
        return (player, owgr_rankings.get(player.replace('.', '').replace('-', '')))

    if owgr_rankings.get(decode(player)):
        if log:
            print ('unidecoded name dict match: ', player, owgr_rankings.get(decode(player)))
        return (player, owgr_rankings.get(decode(player)))

    #lower = {k:v for k,v in owgr_rankings.items() if player.lower() == k.lower()}
    lower = [v for k,v in owgr_rankings.items() if player.lower() == k.lower()]
    if len(lower) > 0:
        return (player, lower[0])

    replace_list = ['-', "'"]
    for char in replace_list:
        strip  = [v for k,v in owgr_rankings.items() if player.replace(char, '').lower() == k.replace(char, '').lower()]
        if len(strip) > 0:
            return (player, strip[0])

    if log:
        print (['player', player])
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
        #elif len(owgr_name) - 1 == len(pga_name) or len(owgr_name) == len(pga_name) - 1 \
        #    and (owgr_name[0] == pga_name[0] \
        #    and decode(owgr_name[len(owgr_name) -1]) == decode(pga_name[len(pga_name) -1])):
        #    print ('strip middle stuff, first and last match', pga_name, owgr_name)
        #    return k, v


        elif decode(owgr_name[len(owgr_name)-2]) == decode(pga_name[len(pga_name)-1]) \
            and k.split(' ')[0] == player.split(' ')[0]:
            #and k[0:1] == player[0:1]:  initial logic checks for charaacter of first name so causing false positives
            if log:
                print ('XXXXX fix this for dru love')
                print ('last name, first initial match, cut owgr suffix', k, v, player, owgr_name)
            return k, v
        #elif len(owgr_name) == 3 and len(pga_name) == 3 and unidecode.unidecode(owgr_name[len(owgr_name)-2]) == unidecode.unidecode(pga_name[len(pga_name)-2]) \
        #    and unidecode.unidecode(owgr_name[0]) == unidecode.unidecode(pga_name[0]):
        #    print ('last name, first name, cut both suffix', player)
        #    return k, v
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


    # s_name = [v for k, v in owgr_rankings.items() if k.split('(')[0] == player.split('(')[0]]
    # if len(s_name) ==1:
    #     print ('split from ( match: ', player, s_name[0])
    #     return (player, s_name[0])

    

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

    
    
        

