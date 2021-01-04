from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.models import modelformset_factory
from fb_app.models import Games, Picks, Teams, Week, PlayoffPicks
#from dal import autocomplete
from django_select2 import *
from django_select2.forms import ModelSelect2Widget
from django.forms.formsets import BaseFormSet




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
        #self.fields['week'].queryset = Week.objects.filter(season_model__current=True)


    class Meta:
        model = Picks
        fields = ('team', )
        

class CreatePlayoffsForm(ModelForm):
    #team = forms.ModelChoiceField(queryset=Teams.objects.all(), widget=Select2Widget)

    def __init__(self, *args, **kwargs):
        super (CreatePlayoffsForm, self).__init__(*args, **kwargs)
        game = Games.objects.get(eid='202017DETMIN')
        teams_list = [game.home.nfl_abbr, game.away.nfl_abbr]
        self.fields['winning_team'].queryset = Teams.objects.filter(nfl_abbr__in=teams_list)
        self.fields['player'].widget = forms.HiddenInput()
        self.fields['game'].widget = forms.HiddenInput()
        
        self.fields['rushing_yards'].label = "Rushing yards:  (total both teams - actual)"
        self.fields['rushing_yards'].widget.attrs['placeholder'] = "Total rushing yards, sum both teams"
        
        self.fields['passing_yards'].label = "Passing yards:  (total both teams - actual)"
        self.fields['passing_yards'].widget.attrs['placeholder'] = "Total passing yards, sum both teams"
        
        self.fields['total_points_scored'].label = "Total Points:  (total both teams - actual) x 5"
        self.fields['total_points_scored'].widget.attrs['placeholder'] = "Sum of total points, both teams"
        
        self.fields['points_on_fg'].label = "Points from FG's:  (total both teams FG's - actual) x 5"
        self.fields['points_on_fg'].widget.attrs['placeholder'] = "Sum of points from FG's"
        
        self.fields['takeaways'].label = "Take aways:  (total both teams takeaways - actual) x 20"
        self.fields['takeaways'].widget.attrs['placeholder'] = "Sum of takeaways, both teams"
        
        self.fields['sacks'].label = "Sum of sacks:  (total both teams sacks - actual) x 20"
        self.fields['sacks'].widget.attrs['placeholder'] = "Sum of sacks, both teams"
        
        self.fields['def_special_teams_tds'].label = "Sum of D/ST TD's:  (total both teams D/ST TD's  - actual) x 50"
        self.fields['def_special_teams_tds'].widget.attrs['placeholder'] = "Sum of D/ST TD's, both teams"
        
        self.fields['team_one_runner'].label = "Top rusher: (home team top rushing yards - actual) x 3"
        self.fields['team_one_runner'].widget.attrs['placeholder'] = "Top rusher yards, home team"
        
        self.fields['team_one_receiver'].label = "Top receiver: (home team top receiving yards - actual) x 3"
        self.fields['team_one_receiver'].widget.attrs['placeholder'] = "Top receiver yards, home team"

        self.fields['team_one_passing'].label = "Top passer: (home team top passing yards - actual) x 3"
        self.fields['team_one_passing'].widget.attrs['placeholder'] = "Top passing yards, home team"

        self.fields['team_two_runner'].label = "Top rusher: (away team top rushing yards - actual) x 3"
        self.fields['team_two_runner'].widget.attrs['placeholder'] = "Top rusher yards, away team"
        
        self.fields['team_two_receiver'].label = "Top receiver: (away team top receiving yards - actual) x 3"
        self.fields['team_two_receiver'].widget.attrs['placeholder'] = "Top receive yards, away team"

        self.fields['team_two_passing'].label = "Top passer: (away team top passing yards - actual) x 3"
        self.fields['team_two_passing'].widget.attrs['placeholder'] = "Top passing yards, away team"










    class Meta:
        model = PlayoffPicks
        fields =  '__all__'



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
