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


def formatRank(rank):
    from golf_app.models import Tournament
    '''takes in a sting and returns a string formatted for the right display or calc.  '''
    t = Tournament.objects.get(current=True)
    #if rank in t.not_playing_list():
    #    return 999
    #print (type(rank), rank)
    if type(rank) is int:
        return rank
    elif rank in  ['', '--', None] or rank in t.not_playing_list():
       return 999
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
        return (name.strip(', Jr.').strip(',Jr ').strip(', Jr.').strip('(a)').strip(',').strip('Jr.'))
