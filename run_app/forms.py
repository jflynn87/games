from django import forms
from django.forms import ModelForm
from run_app.models import Shoes, Run

class CreateShoeForm(ModelForm):
    model= Shoes

class DateInput(forms.DateInput):
    input_type = 'date'

class CreateRunForm(ModelForm):

    class Meta:
        model = Run
        fields = ('__all__')
        widgets = {
            'date': DateInput(),
        }

    def __init__(self, *args, **kwargs):
        super(CreateRunForm, self).__init__(*args, **kwargs)
        self.fields['shoes'].queryset = Shoes.objects.filter(active=True)
