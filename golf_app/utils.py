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
    '''takes in a sting and returns a string formatted for the right display or calc'''

    if type(rank) is int:
        return rank
    elif rank in  ['', '--', None]:
       return 0
    elif rank[0] != 'T':
       return int(rank)
    elif rank[0] == 'T':
       return int(rank[1:])
    else:
       return int(rank)

def format_name(name):
    '''take a name string and match pga conventions '''
    if len(name.split(' ')) == 2:
        return name
    else:
        print (name.split(' '))
        return (name.strip(', Jr.').strip(',Jr ').strip(', Jr.').strip('(a)').strip(',').strip('Jr.'))
