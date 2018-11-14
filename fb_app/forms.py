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


    class Meta:
        model = Picks
        fields = ('team',)
        team = forms.ModelChoiceField(queryset=Teams.objects.all(),
        widget = ModelSelect2Widget)

week = Week.objects.get(current=True)
print (week.week, week.game_cnt)
PickFormSet = modelformset_factory(Picks, form=CreatePicksForm, max_num=(week.game_cnt))
NoPickFormSet = modelformset_factory(Picks, form=CreatePicksForm, extra=(week.game_cnt))


# class PickFormSet(BaseModelFormSet):
#     absolute_max = 16
#     min_num = 12
#     form = CreatePicksForm
#     can_order=False
#     can_delete=False
#     validate_max = False
#     validate_min =False


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
