from rest_framework import serializers
import json
from golf_app.models import Field, ScoreDetails, Golfer, CountryPicks
from golf_app import espn_api

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
    #started = serializers.SerializerMethodField('get_started')

    class Meta:
        model = Field
        fields = '__all__'
        depth = 1

    def get_espn_link(self, field):
        return field.golfer.espn_link()

    def get_pga_link(self, field):
        return field.golfer.get_pga_player_link()

    def get_started(self, field):
        obj = espn_api.ESPNData(data=self.context.get('espn_data'))
        started = obj.player_started(field.golfer.espn_number)
        return started

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
