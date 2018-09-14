from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from fb_app.models import Games, Picks, Teams
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

    #def __init__(self, *args, **kwargs):
    #    super (CreatePicksForm, self).__init__(*args,**kwargs)
    #    self.fields['team'].required =True
    #    print (user)




    #def clean(self):
    #    cleaned_data = super(CreatePicksForm, self).clean()
    #    return cleaned_data


class PickFormSet(BaseFormSet):
    absolute_max = 16
    min_num = 12
    form = CreatePicksForm
    can_order=False
    can_delete=False
    validate_max = False
    validate_min =False

    #def clean(self):

    #    cleaned_data = super(PickFormSet, self).clean()
    #    print ('clean set')
    #    print (cleaned_data)
    #    #self.add_error('team',"Please picks errors")
    #    return cleaned_data
                    #def clean(self):
                #    cleaned_data = super(AppointmentForm, self).clean()
                #    print (cleaned_data['date'])
                #    if self.cleaned_data.get('date') == None and self.cleaned_data.get('comments') == '':
                #        self.add_error('comments',"Please enter either a message or a meeting date/time")
                #        #return forms.ValidationError('Please enter either a message or a meeting date/time')
                #    else:
                #        return cleaned_data



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
