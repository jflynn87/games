from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from fb_app.models import Games, Picks, Teams, Week
#from dal import autocomplete
from django_select2 import *
from django_select2.forms import ModelSelect2Widget
from django.forms.formsets import BaseFormSet




class CreatePicksForm(ModelForm):
    #team = forms.ModelChoiceField(queryset=Teams.objects.all(), widget=Select2Widget)

    def __init__(self, *args, **kwargs):
        super (CreatePicksForm, self).__init__(*args, **kwargs)
        team_list = []
        for game in Games.objects.filter(week__current=True):
            team_list.append(game.home)
            team_list.append(game.away)
        self.fields['team'].queryset = Teams.objects.filter(nfl_abbr__in=team_list)
        self.fields['week'].queryset = Week.objects.filter(season_model__current=True)
    

    class Meta:
        model = Picks
        fields = ('team','week')



class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())



    class Meta():
        model = User
        fields = ('username', 'email', 'password')


    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "passwords don't not match, please try again")
