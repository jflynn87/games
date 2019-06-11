from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from port_app.models import Position
from django.db.models import Max
from django.forms.models import modelformset_factory

from django_select2.forms import ModelSelect2Widget
from django.forms.formsets import BaseFormSet

class DateInput(forms.DateInput):
    input_type = 'date'

class CreatePositionForm(forms.ModelForm):
    class Meta:
        model=Position
        fields = '__all__'
        #exclude = ("symbol",)
        widgets = {'open_date': DateInput(),
                'close_date': DateInput(),
                }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['close_date'].required=False
        self.fields['notes'].required = False
#        self.fields['open_date'].widget.attrs({'datepicker'})
