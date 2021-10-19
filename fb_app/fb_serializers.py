from rest_framework import serializers
from fb_app.models import Picks



#class PicksSerializer(serializers.Serializer):
class PicksSerializer(serializers.ModelSerializer):
    loser = serializers.SerializerMethodField('get_loser')

    class Meta:
        model = Picks
        #fields = '__all__'
        fields = ['player', 'team', 'loser']
        depth = 1   
        read_only_field = fields

    def get_loser(self, obj):
        return obj.is_loser()
