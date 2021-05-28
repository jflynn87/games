from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from golf_app.models import  Field, Picks, Group, Tournament, AuctionPick
from django.db.models import Max
from django.forms.models import modelformset_factory
#from django_select2 import *
#from django_select2.forms import ModelSelect2Widget
from django.forms.formsets import BaseFormSet
from golf_app import manual_score
#from extra_views import ModelFormSetView

class CreateManualScoresForm(forms.ModelForm):

    class Meta:
        model = Picks
        fields = ('playerName', 'score',)

class FieldForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        t = Tournament.objects.get(current=True)
        super(FieldForm, self).__init__(*args, **kwargs)
        self.fields['group'].queryset = Group.objects.filter(tournament=t)
        self.fields['group'].label = ''
        self.fields['playerName'].label = ''
        self.fields['playerName'].disabled = True
        

    class Meta:
        model = Field    
        fields = ['playerName', 'group',]

FieldFormSet = modelformset_factory(Field, form=FieldForm, min_num=1, max_num=156, extra=0)


class AuctionPickForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(AuctionPickForm, self).__init__(*args, **kwargs)
        self.fields['playerName'].queryset = Field.objects.filter(tournament__current=True)
        self.fields['user'].queryset = User.objects.filter(username__in=['john', 'jcarl62', 'ryosuke'])


    class Meta:
        model = AuctionPick
        fields = '__all__'



AuctionPicksFormSet = modelformset_factory(AuctionPick, form=AuctionPickForm, min_num=3, max_num=3, extra=0)


#class SinglePickGroupForm(forms.ModelForm):

#     class Meta:
#         model = Picks
#         fields = ('playerName',)
#         playerName = forms.ModelChoiceField(queryset=Field.objects.filter(tournament__current=True),
         #playerName = forms.ModelChoiceField(queryset=Field.objects.all(),
#         widget = forms.RadioSelect)
#
#
# group_cnt = Group.objects.filter(tournament__current=True).aggregate(Max('number'))
# print ('group_cnt', group_cnt)
#PickFormSet = modelformset_factory(Picks, form=SinglePickGroupForm, max_num=group_cnt.get('number_max'))
# NoPickFormSet = modelformset_factory(Picks, form=CreatePicksForm, extra=group_cnt.get('number_max'))



# class CreatePicksForm(forms.ModelForm):
#      #CHOICES = get_choices()
#      playerName = forms.ModelChoiceField(queryset=Field.objects.all(), widget=forms.RadioSelect())
#      model = Field
#
#      def get_choices(self):
#          field = Field.objects.all()
#          choice_list = []
#
#          for group in field:
#              choice_list.append(group.group)
#              for player in group:
#                  palyers = players + player.playerName
#              choice_list.append(players)
#          print (player_list)
#          return player_list
