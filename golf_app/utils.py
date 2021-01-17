import unidecode

def format_score(score):
    '''takes in a sting and returns a string formatted for the right display or calc'''
    if score == None:
        return "not started"
    if score == 0:
        return 'even'
    elif score > 0:
        return ('+' + str(score))
    else:
        return score


def formatRank(rank, tournament=None):
    from golf_app.models import Tournament
    '''takes in a sting and returns a string formatted for the right display or calc.  '''
    t = Tournament.objects.get(current=True)
    #if rank in t.not_playing_list():
    #    return 999
    #print (type(rank), rank)
    if type(rank) is int:
        return rank
    elif rank in  ['', '--', None] or rank in t.not_playing_list():
       #return 999
       if t == None:
           return 999
       else:
           return t.saved_cut_num 
    elif rank[0] != 'T':
       return int(rank)
    elif rank[0] == 'T':
       return int(rank[1:])
    else:
       return rank

def format_name(name):
    '''take a name string and match pga conventions '''
    if len(name.split(' ')) == 2:
        return name
    else:
        print (name.split(' '))
        return (name.strip(', Jr.').strip(',Jr ').strip('(a)').strip(',').strip('Jr.').strip('.'))


def fix_name(player, owgr_rankings):
    '''takes a string and a dict and returns a dict?'''
    print ('trying to fix name: ', player)
    
    if owgr_rankings.get(player) != None:
        return (owgr_rankings.get(player))

    print (player.replace(',', '').split(' '))
    for k, v in owgr_rankings.items():
        owgr_name = k.replace(',', '').split(' ')
        pga_name = player.replace(',', '').split(' ')
        #print (owgr_name, pga_name)
        
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
    print ('didnt find match', pga_name)
    return None, [9999, 9999, 9999]
