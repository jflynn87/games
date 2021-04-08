import unidecode
from datetime import datetime

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
    '''takes in a sting and returns an int'''
    
    t = Tournament.objects.get(current=True)
    
    if type(rank) is int:
        return rank
    elif rank in  ['', '--', '-', None] or rank in t.not_playing_list():
       if t == None:
           return 999
       else:
           return t.saved_cut_num 
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


def fix_name(player, owgr_rankings):
    '''takes a string and a dict and returns a dict?'''
    #print ('trying to fix name: ', player)
    #print (player, ' :  ', owgr_rankings)    
    if owgr_rankings.get(player) != None:
        print ('name dict match: ', owgr_rankings.get(player))
        return (player, owgr_rankings.get(player))

    if owgr_rankings.get(unidecode.unidecode(player)):
        print ('unidecoded name dict match: ', player, owgr_rankings.get(unidecode.unidecode(player)))
        return (player, owgr_rankings.get(unidecode.unidecode(player)))

    #print (player.replace(',', '').split(' '))
    
    pga_name = player.replace(' (a)', '').replace(',', '').split(' ')
    print ('input name: ', player)
    print ('pga name for compare: ', pga_name)

    for k, v in owgr_rankings.items():
        
        owgr_name = k.replace(',', '').split(' ').remove(' ')
        print (owgr_name)
        if '(' in owgr_name[len(owgr_name)-1] and owgr_name[len(owgr_name)-2] == '':
            del owgr_name[len(owgr_name)-1]
            del owgr_name[len(owgr_name)-1]
            if owgr_rankings == player.replace(',', '').split(' '):
                return k, v
        
        if unidecode.unidecode(owgr_name[len(owgr_name)-1]) == unidecode.unidecode(pga_name[len(pga_name)-1]) \
           and k[0:1] == player[0:1]:
            print ('last name, first initial match', player)
            return k, v
        elif len(owgr_name) == 3 and len(pga_name) == 3 and unidecode.unidecode(owgr_name[0]) == unidecode.unidecode(pga_name[0]) \
            and unidecode.unidecode(owgr_name[2]) == unidecode.unidecode(pga_name[2]) and owgr_name[1][0] == pga_name[1][0]:
                print ('last name, first name match, middle first intial match', player)
                return k, v
       
        elif len(owgr_name[3]) < 4 and unidecode.unidecode(owgr_name[len(owgr_name)-2]) == unidecode.unidecode(pga_name[len(pga_name)-1]) \
            and k[0:1] == player[0:1]:
            print ('last name, first initial match, cut owgr suffix', player)
            return k, v
        elif len(owgr_name) == 3 and len(pga_name) == 3 and unidecode.unidecode(owgr_name[len(owgr_name)-2]) == unidecode.unidecode(pga_name[len(pga_name)-2]) \
            and unidecode.unidecode(owgr_name[0]) == unidecode.unidecode(pga_name[0]):
            print ('last name, first name, cut both suffix', player)
            return k, v
        elif unidecode.unidecode(owgr_name[0]) == unidecode.unidecode(pga_name[len(pga_name)-1]) \
            and unidecode.unidecode(owgr_name[len(owgr_name)-1]) == unidecode.unidecode(pga_name[0]):
            print ('names reversed', player)
            return k, v

    s_name = [v for k, v in owgr_rankings.items() if k.split('(')[0] == player.split('(')[0]]
    if len(s_name) ==1:
        print ('split from ( match: ', player, s_name[0])
        return (player, s_name[0])

    

    print ('didnt find match', player)
    return None, [9999, 9999, 9999]


def check_t_names(espn_t, t):
    '''Takes a string and a tournament object and returns a bool'''
    espn_name = espn_t.lower().split(' ')
    pga_name = t.name.lower().split(' ')
    print ('espn name: ', espn_name)
    print ('pga name: ', pga_name)
    matches = len([x for x in pga_name if x in espn_name])
    print ('matches: ', matches == len(espn_name) -1, espn_name[1], type(espn_name[1]))
    if len(pga_name) < 4 and espn_name == pga_name:
        return True
    #added below for masters, could be better
    elif espn_name[0] == '2021' and matches == len(espn_name) -1:
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