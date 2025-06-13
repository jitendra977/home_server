from django import forms
from .models import Appliance

class ApplianceForm(forms.ModelForm):
    class Meta:
        model = Appliance
        fields = ['name', 'location', 'status', 'room', 'user']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Device Name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Room/Location'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
    def clean_name(self):
            name = self.cleaned_data['name']
            if len(name)< 3:
                raise forms.ValidationError("Device name must be 3 character !!")
            return name