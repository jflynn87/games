from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from fb_app.models import Games, Picks, Teams, Week, PlayoffPicks, SeasonPicks

from django_select2 import *
from django_select2.forms import ModelSelect2Widget
from django.forms.formsets import BaseFormSet
from django.core.exceptions import ValidationError





class CreatePicksForm(ModelForm):
    #team = forms.ModelChoiceField(queryset=Teams.objects.all(), widget=Select2Widget)

    def __init__(self, week, *args, **kwargs):
        super (CreatePicksForm, self).__init__(*args, **kwargs)
        team_list = []
        #self.fields['week'] = week
        for game in Games.objects.filter(week=week).order_by('game_time'):
        #for game in Games.objects.filter(week__current=True).order_by('game_time'):
            team_list.append(game.home)
            team_list.append(game.away)
        self.fields['team'].queryset = Teams.objects.filter(nfl_abbr__in=team_list)


    class Meta:
        model = Picks
        fields = ('team', )
        

class CreatePlayoffsForm(ModelForm):

    class Meta:
        model = PlayoffPicks
        exclude =  ['player', 'game', 'home_passing', 'away_passing', 'rushing_yards', 'passing_yards']
        #widgets = {'winning_team': forms.RadioSelect()}  #not sure why this stopped working

    def __init__(self, *args, **kwargs):
        super (CreatePlayoffsForm, self).__init__(*args, **kwargs)
        game = Games.objects.get(week__current=True, playoff_picks=True)
        teams_list = [game.home, game.away]
        self.fields['winning_team'].queryset = Teams.objects.filter(nfl_abbr__in=teams_list)
        self.fields['winning_team'].label = "Winning Team - 1 point for the Fav, 2 for the Dog"
        
        self.fields['total_points_scored'].label = "Total Points Scored - both teams"
        self.fields['total_points_scored'].widget.attrs['placeholder'] = "Sum of total points, both teams"
        
        self.fields['points_on_fg'].label = "Points from FG's - both teams"
        self.fields['points_on_fg'].widget.attrs['placeholder'] = "Sum of points from FG's"
        
        self.fields['takeaways'].label = "Take aways - total both teams"
        self.fields['takeaways'].widget.attrs['placeholder'] = "Sum of takeaways, both teams"
        
        self.fields['sacks'].label = "Sum of sacks - both teams"
        self.fields['sacks'].widget.attrs['placeholder'] = "Sum of sacks, both teams"
        
        self.fields['def_special_teams_tds'].label = "Sum of D/ST TD's - both teams"
        self.fields['def_special_teams_tds'].widget.attrs['placeholder'] = "Sum of D/ST TD's, both teams"
        
        self.fields['home_runner'].label =  game.home.long_name + " top rusher yards"
        self.fields['home_runner'].widget.attrs['placeholder'] = "Top rusher yards, home team"
        
        self.fields['home_receiver'].label = game.home.long_name + " top receiver yards"
        self.fields['home_receiver'].widget.attrs['placeholder'] = "Top receiver yards, home team"

        self.fields['home_passer_rating'].label = game.home.long_name + " top passer rating *"
        self.fields['home_passer_rating'].widget.attrs['placeholder'] = "Top passer rating, home team"

        self.fields['away_runner'].label =  game.away.long_name + " top rusher yards"
        self.fields['away_runner'].widget.attrs['placeholder'] = "Top rusher yards, away team"
        
        self.fields['away_receiver'].label = game.away.long_name + " top receiver yards"
        self.fields['away_receiver'].widget.attrs['placeholder'] = "Top receiving yards, away team"

        self.fields['away_passer_rating'].label = game.away.long_name + " top passer rating *"
        self.fields['away_passer_rating'].intial = ''
        self.fields['away_passer_rating'].widget.attrs['placeholder'] = "Top passer rating," + game.away.nfl_abbr + "value between 0 - 158.3"


    def clean_points_on_fg(self):
        data = self.cleaned_data['points_on_fg']
        if not data % 3 == 0:
            raise ValidationError("FG points should be divisible by 3") 
        return data

    def clean_home_passer_rating(self):
        data = self.cleaned_data['home_passer_rating']
        if not data > 0 and not data < 158.33:
            raise ValidationError("Rating must be between 0 - 158.33") 
        return data

    def clean_away_passer_rating(self):
        data = self.cleaned_data['away_passer_rating']
        if not data >0 and data < 158.33:
            raise ValidationError("Rating must be between 0 - 158.33") 
        return data


class CreateSeasonPicksForm(ModelForm):

    class Meta:
        model = SeasonPicks
        fields = ('pick',)
        #exclude =  ['player', 'game', 'home_passing', 'away_passing', 'rushing_yards', 'passing_yards']
        #widgets = {'winning_team': forms.RadioSelect()}
    
    def __init__(self, *args, **kwargs):
        super (CreateSeasonPicksForm, self).__init__(*args, **kwargs)
        #picks = Games.objects.get(week__current=True, playoff_picks=True)
        #self.fields['pick'].queryset = 


SeasonPicksFormSet = modelformset_factory(SeasonPicks, form=CreateSeasonPicksForm, min_num=1, max_num=156, extra=0)

# class UserForm(forms.ModelForm):
#     password = forms.CharField(widget=forms.PasswordInput())
#     confirm_password = forms.CharField(widget=forms.PasswordInput())



#     class Meta():
#         model = User
#         fields = ('username', 'email', 'password')


#     def clean(self):
#         cleaned_data = super(UserForm, self).clean()
#         password = cleaned_data.get("password")
#         confirm_password = cleaned_data.get("confirm_password")

#         if password != confirm_password:
#             raise forms.ValidationError(
#                 "passwords don't not match, please try again")
