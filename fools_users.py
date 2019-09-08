import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","gamesProj.settings")

import django
django.setup()
from fb_app.models import User, Player, League



def load_users():

    league = League.objects.get(league="Football Fools")
    
    user_list = ['NU', 'JABO', 'TLUKE', 'CAKE', 'WHEEL', 'DMC', 'NORM', 'NITNY', 'HANK', 'ADOLF',
    	'CU', 'MILT', 'OB', 'SQUIG', 'TOKYO', 'LEFTY', 'FSU', 'SIEG', 'JB', 'LI’L B', 'BAKER', 
        'ODELL', '4JULY', 'KEY LARGO', 'NJN EER', 'ESPN PALS']     

    old_user_list=['NU', 'JABO',	'CAKE',	'Wheel', 'DMC',	'NORM',	'NITNY', 'HANK',
	   'ADOLF', 'CU', 'MILT', 'OB', 'SQUIG', 'TOKYO', 'LEFTY', 'FSU', 'SIEG',
       'JB', 'LiL B', 'WHALE', 'SLIM', '4JULY',	'KEY LARGO', 'NJN EER', 'ESPN PALS']

    for user in old_user_list:
        try:
            user_obj = User.objects.get(username=user)
            print (user_obj)    
            player = Player.objects.get(name=user_obj, league=league)
            print (player)
            user_obj.username = user + '2018'
            user_obj.save()

            player.name = user_obj
            player.save()



            print (user_obj, player)
        except Exception as e:
            print ('exeception', e, user)
    
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
