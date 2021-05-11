from rest_framework import serializers
import json
from golf_app.models import Field, ScoreDetails

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

    class Meta:
        model = Field
        fields = '__all__'
        depth = 1

    #def get_recent(self, field):
    #    return json.dumps(field.recent)

class ScoreDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreDetails
        fields = '__all__'
        depth = 3
