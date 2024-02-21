from django import forms
from .models import Tdo


class TDOForm(forms.ModelForm):
    class Meta:
        model = Tdo
        fields = [
            'title',
            'description',
            'company'
        ]