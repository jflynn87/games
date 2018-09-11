from django import forms
from django.forms import ModelForm
from run_app.models import Shoes, Run
from datetime import date

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
        self.fields['location'].initial = '1'
        self.fields['shoes'].initial = Shoes.objects.get(main_shoe=True)
        self.fields['date'].initial = date.today()
