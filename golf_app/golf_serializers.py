from rest_framework import serializers
import json
from golf_app.models import Field, ScoreDetails, Golfer, CountryPicks, Picks, Tournament, FedExField, Season, FedExPicks
from golf_app import espn_api
from datetime import datetime

class FieldSerializer(serializers.ModelSerializer):

    prior = serializers.SerializerMethodField('get_prior')
    recent = serializers.SerializerMethodField('get_recent')
    #started = serializers.SerializerMethodField('get_started')

    class Meta:
        model = Field
        fields = '__all__'
        depth = 1
    
    def get_prior(self, field):
        prior = field.prior_year_finish()
        return prior

    def get_recent(self, field):
        recent = field.recent_results()
        return recent
    
    #def get_started(self, field):
    #    started = field.started()
    #    return started

class NewFieldSerializer(serializers.ModelSerializer):

    #recent = serializers.SerializerMethodField('get_recent')
    espn_link = serializers.SerializerMethodField('get_espn_link')
    pga_link = serializers.SerializerMethodField('get_pga_link')
    started = serializers.SerializerMethodField('get_started')
    lock_group = serializers.SerializerMethodField('get_group_lock')
    #user = serializers.SerializerMethodField('get_user')

    class Meta:
        model = Field
        fields = '__all__'
        depth = 2

    def get_espn_link(self, field):
        return field.golfer.espn_link()

    def get_pga_link(self, field):
        return field.golfer.get_pga_player_link()

    def get_started(self, field):
        #used for testing, delete
        #if Picks.objects.filter(user=self.context.get('user'), playerName__playerName=field.playerName, playerName__tournament=field.tournament).exists():
        #if field.playerName in ["Jon Rahm", "Charley Hoffman", "Troy Merritt"] : 
        #        print ('started check A ', field.playerName, True)
        #        return True 
        obj = espn_api.ESPNData(data=self.context.get('espn_data'))
        started = obj.player_started(field.golfer.espn_number)
        #print ('started check ', field.playerName, started)
        return started

    def get_group_lock(self, field):
        group = field.group
        if Picks.objects.filter(user=self.context.get('user'), playerName__group=field.group).exists():
            #if group.num_of_picks == 1 and self.get_started(field):
            #    return True
            #elif group.num_of_picks() > 1:
                started_count = 0
                for p in Picks.objects.filter(user=self.context.get('user'), playerName__group=field.group, playerName__tournament=field.tournament):
                    if self.get_started(Field.objects.get(playerName=p.playerName, tournament=p.playerName.tournament)):
                        started_count += 1
                if started_count == Picks.objects.filter(user=self.context.get('user'), playerName__group=field.group).count():
                    return True
                else:
                    return False
            #elif group.num_of_picks() == 1:
            #    pick = Picks.objects.get(user=self.context.get('user'), playerName__group=field.group)
            #    if self.get_started(field):
            #        return True

        return False



class ScoreDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreDetails
        fields = '__all__'
        depth = 3

class GolferSerializer(serializers.ModelSerializer):
    #season_results = serializers.SerializerMethodField('get_season_results')

    class Meta:
        model = Golfer
        fields = '__all__'
        depth = 1
    
    #def get_season_results(self, golfer):
    #    return golfer.results.

class CountryPicks(serializers.ModelSerializer):
    get_flag = serializers.SerializerMethodField('get_flag_link')

    class Meta:
        model = CountryPicks
        fields = '__all__'
        depth = 1   

    def get_flag_link(self, countrypick):
        return countrypick.get_flag()


# class PlayerStartedSerializer(serializers.ModelSerializer):
#     started = serializers.SerializerMethodField('get_started')
#     #espn_number = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

#     class Meta:
#         model = Field
#         fields = ('golfer__espn_number', 'started')
#         depth = 2

#     def get_started(self, field):
#         obj = espn_api.ESPNData(data=self.context.get('espn_data'))
#         started = obj.player_started(field.golfer.espn_number)
#         return started


class PicksSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Picks
        fields = '__all__'
        depth = 2


class FedExFieldSerializer(serializers.ModelSerializer):
    prior_owgr = serializers.SerializerMethodField('get_prior_owgr')
    picked = serializers.SerializerMethodField('get_picked')

    class Meta:
        model = FedExField
        fields = '__all__'
        depth = 2

    def get_prior_owgr(self, fedexfield):
        c_s = Season.objects.get(current=True)
        season = Season.objects.get(season=str(int(c_s.season)-1))

        f = Field.objects.filter(golfer=fedexfield.golfer, tournament__season=season).exclude(tournament__pga_tournament_num='999').order_by('-pk')[0]

        return f.soy_WGR
    
    def get_picked(self, obj):
        user = self.context.get('user')
        if FedExPicks.objects.filter(pick=obj, user=user).exists():
            return True
        else:
            return False
