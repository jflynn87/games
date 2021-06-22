from rest_framework import serializers
import json
from golf_app.models import Field, ScoreDetails, Golfer

class FieldSerializer(serializers.ModelSerializer):

    prior = serializers.SerializerMethodField('get_prior')
    recent = serializers.SerializerMethodField('get_recent')

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

class NewFieldSerializer(serializers.ModelSerializer):

    #recent = serializers.SerializerMethodField('get_recent')
    espn_link = serializers.SerializerMethodField('get_espn_link')
    pga_link = serializers.SerializerMethodField('get_pga_link')

    class Meta:
        model = Field
        fields = '__all__'
        depth = 1

    def get_espn_link(self, field):
        return field.golfer.espn_link()

    def get_pga_link(self, field):
        return field.golfer.golfer_link()


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
