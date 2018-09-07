import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import User, Player, League



def load_users():

    user_list=['NU', 'JABO',	'CAKE',	'Wheel', 'DMC',	'NORM',	'NITNY', 'HANK',
	   'ADOLF', 'CU', 'MILT', 'OB', 'SQUIG', 'TOKYO', 'LEFTY', 'FSU', 'SIEG',
       'JB', 'LiL B', 'WHALE', 'SLIM', '4JULY',	'KEY LARGO', 'NJN EER', 'ESPN PALS']

    for userID in user_list:
        user=User()
        user.username=userID
        user.save()
        #league = League.objects.get(league='Football Fools')
        league = League.objects.get(league="Football Fools")

        player=Player()
        player.league = league
        player.name = user
        player.save()




if __name__ == '__main__':
    print ('populating script!')
    #clean_db()
    load_users()
    print ("Populating Complete!")
