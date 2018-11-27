from django import forms
from django.forms import ModelForm
from run_app.models import Shoes, Run
from datetime import date
from django.core.exceptions import ObjectDoesNotExist

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

    def clean(self):
        cd = super(CreateRunForm, self).clean()
        try:
            Run.objects.get(date=cd['date'])
            raise forms.ValidationError('A run already exists for that date')
        except ObjectDoesNotExist:
            pass

        return cd
