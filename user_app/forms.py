from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm



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


class UserCreateForm(UserCreationForm):
    class Meta:
        fields = ('username', 'email', 'password1', 'password2',)
        model = get_user_model()


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label= "Display Name"
        self.fields['email'].label = "Email Address"
        self.fields['email'].help_text = '* Only used if you need to reset your password'
        self.fields['username'].help_text = '* You can use your real name or a nickname'
        self.fields['password1'].help_text = "* Password must be 8 characters"
        self.fields['password2'].help_text = "* Enter the same password as before, for verification."

