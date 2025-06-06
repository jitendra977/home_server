from django import forms
from .models import Appliance

class ApplianceForm(forms.ModelForm):
    class Meta:
        model = Appliance
        fields = ['name', 'location', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Device Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room/Location'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }