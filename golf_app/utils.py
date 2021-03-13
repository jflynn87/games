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

def score_as_int(score):
    if score is int:
        return score
    elif score == "E":
        return 0
    elif len(score) > 1 and score[0] in ['+', '-']:
        return score
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

    print (player.replace(',', '').split(' '))
    
    for k, v in owgr_rankings.items():
        owgr_name = k.replace(',', '').split(' ')
        if '(' in owgr_name[len(owgr_name)-1] and owgr_name[len(owgr_name)-2] == '':
            del owgr_name[len(owgr_name)-1]
            del owgr_name[len(owgr_name)-1]
            if owgr_rankings == player.replace(',', '').split(' '):
                return k, v
        
        pga_name = player.replace(',', '').split(' ')
        
        if unidecode.unidecode(owgr_name[len(owgr_name)-1]) == unidecode.unidecode(pga_name[len(pga_name)-1]) \
           and k[0:1] == player[0:1]:
            print ('last name, first initial match', player)
            return k, v
        elif unidecode.unidecode(owgr_name[len(owgr_name)-2]) == unidecode.unidecode(pga_name[len(pga_name)-1]) \
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

    print ('didnt find match', player)
    return None, [9999, 9999, 9999]


def check_t_names(espn_t, t):
    '''Takes a string and a tournament object and returns a bool'''
    espn_name = espn_t.lower().split(' ')
    pga_name = t.name.lower().split(' ')
    print ('espn name: ', espn_name)
    print ('pga name: ', pga_name)
    matches = len([x for x in pga_name if x in espn_name])
    if matches < len(pga_name)/2:
        return False
    else:
        return True

