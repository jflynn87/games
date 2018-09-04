from django import forms
from django.contrib.auth.models import User
from golf_app.models import  Field, Picks


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


class CreatePicksForm(forms.ModelForm):
     #CHOICES = get_choices()
     playerName = forms.ModelChoiceField(queryset=Field.objects.all(), widget=forms.RadioSelect())
     model = Field

     def get_choices(self):
         field = Field.objects.all()
         choice_list = []

         for group in field:
             choice_list.append(group.group)
             for player in group:
                 palyers = players + player.playerName
             choice_list.append(players)
         print (player_list)
         return player_list
