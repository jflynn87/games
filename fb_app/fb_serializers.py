from rest_framework import serializers
from fb_app.models import Picks



#class PicksSerializer(serializers.Serializer):
class PicksSerializer(serializers.ModelSerializer):

    class Meta:
        model = Picks
        fields = '__all__'
        depth = 1
        read_only_field = fields
