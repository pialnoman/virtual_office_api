from django import forms
from .models import Slc, HourType
from datetime import datetime

class CustomAddSLCForm(forms.ModelForm):
    class Meta:
        model = Slc
        fields = [
            'employee',
            'slc',
            'monthly_rate',
            'hourly_rate',
            'hourly_rate'
        ]

class CustomEditSLCForm(forms.ModelForm):
    class Meta:
        model = Slc
        fields = [
            'slc',
            'monthly_rate',
            'hourly_rate',
            'hourly_rate'
        ]


class HourTypeForm(forms.ModelForm):
    class Meta:
        model = HourType
        fields = [
            'title',
            'year',
            'description',
            'hours_allocated',
        ]