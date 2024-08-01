from rest_framework import serializers

from golf_app.models import Field, ScoreDetails, Golfer, CountryPicks, Picks, Tournament, FedExField, Season, FedExPicks, BonusDetails, PickMethod
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

class PreStartFieldSerializer(serializers.ModelSerializer):

    espn_link = serializers.SerializerMethodField('get_espn_link')
    pga_link = serializers.SerializerMethodField('get_pga_link')
    fedex_pick = serializers.SerializerMethodField('get_fedex')

    class Meta:
        model = Field
        fields = '__all__'
        depth = 1  
        

    def get_espn_link(self, field):
        return field.golfer.espn_link()

    def get_pga_link(self, field):
        return field.golfer.get_pga_player_link()

    def get_fedex(self, field):
        user = self.context.get('user')
        return field.fedex_pick(user)


class NewFieldSerializer(serializers.ModelSerializer):

    espn_link = serializers.SerializerMethodField('get_espn_link')
    pga_link = serializers.SerializerMethodField('get_pga_link')
    started = serializers.SerializerMethodField('get_started')
    lock_group = serializers.SerializerMethodField('get_group_lock')
    fedex_pick = serializers.SerializerMethodField('get_fedex')

    class Meta:
        model = Field
        fields = '__all__'
        depth = 1  #changed from 2 to speed up field load
        

    def get_espn_link(self, field):
        return field.golfer.espn_link()

    def get_pga_link(self, field):
        return field.golfer.get_pga_player_link()

    def get_started(self, field):
        start = datetime.now()
        espn = self.context.get('espn_data')
        started = espn.player_started(field.golfer.espn_number)
        return started

    def get_group_lock(self, field):
        start = datetime.now()

        if Picks.objects.filter(user=self.context.get('user'), playerName__group=field.group).exists():
                started_count = 0
                for p in Picks.objects.filter(user=self.context.get('user'), playerName__group=field.group, playerName__tournament=field.tournament):
                    if self.get_started(Field.objects.get(playerName=p.playerName, tournament=p.playerName.tournament)):
                        started_count += 1
                if started_count == Picks.objects.filter(user=self.context.get('user'), playerName__group=field.group).count():
                    return True
                else:
                    return False
        return False


    def get_fedex(self, field):
        user = self.context.get('user')
        return field.fedex_pick(user)


class ScoreDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreDetails
        fields = '__all__'
        depth = 3  

class SDOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreDetails
        fields = '__all__'
        #depth = 3  commented on 1/8/22 as part of testing api scores
        depth = 1


class GolferSerializer(serializers.ModelSerializer):
    #season_results = serializers.SerializerMethodField('get_season_results')
    espn_link = serializers.SerializerMethodField('get_espn_link')
    pga_link =  serializers.SerializerMethodField('get_pga_link')

    class Meta:
        model = Golfer
        fields = '__all__'
        depth = 1
    
    def get_espn_link(self, golfer):
        return golfer.espn_link()

    def get_pga_link(self, golfer):
        return golfer.get_pga_player_link()


class CountryPicks(serializers.ModelSerializer):
    flag_link = serializers.SerializerMethodField('get_flag_link')
    user_name = serializers.SerializerMethodField('get_user_name')

    class Meta:
        model = CountryPicks
        fields = '__all__'
        #depth = 1   

    def get_flag_link(self, country):
        return country.get_flag()
    
    def get_user_name(self, country):
        return country.user.username


class PicksSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Picks
        fields = '__all__'
        depth = 2


class FedExFieldSerializer(serializers.ModelSerializer):
    #prior_owgr = serializers.SerializerMethodField('get_prior_owgr')
    picked = serializers.SerializerMethodField('get_picked')
    top_3 = serializers.SerializerMethodField('get_top3')

    class Meta:
        model = FedExField
        fields = '__all__'
        depth = 2

    def get_prior_owgr(self, fedexfield):
        c_s = Season.objects.get(current=True)
        season = Season.objects.get(season=str(int(c_s.season)-1))

        if Field.objects.filter(golfer=fedexfield.golfer, tournament__season=season).exclude(tournament__pga_tournament_num='999').exists():
            f = Field.objects.filter(golfer=fedexfield.golfer, tournament__season=season).exclude(tournament__pga_tournament_num='999').order_by('-pk')[0]
            return f.soy_WGR
        else:
            return '9999'

        
    
    def get_picked(self, obj):
        user = self.context.get('user')
        if FedExPicks.objects.filter(pick=obj, user=user).exists():
            return True
        else:
            return False

    def get_top3(self, obj):
        user = self.context.get('user')
        if FedExPicks.objects.filter(pick=obj, user=user).exists():
            p = FedExPicks.objects.get(pick=obj, user=user)
            if p.top_3:
                return True
            else:
                return False
        else:
            return False


class FedExPicksSerializer(serializers.ModelSerializer):

    class Meta:
        model = FedExPicks
        fields = '__all__'
        depth = 1

class BonusDetailSerializer(serializers.ModelSerializer):
    bonus_type_desc = serializers.SerializerMethodField('get_desc')

    class Meta:
        model = BonusDetails
        fields = '__all__'
        depth = 2

    def get_desc(self, bd):
        return bd.get_bonus_type_display()

class PickMethodSerializer(serializers.ModelSerializer):

    class Meta:
        model = PickMethod
        fields = '__all__'
        depth = 1
