# appliances/forms.py

from django import forms
from .models import Appliance

class ApplianceForm(forms.ModelForm):
    class Meta:
        model = Appliance
        fields = ['name', 'location', 'room', 'user', 'device_type', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-4 bg-white/70 dark:bg-black/30 border-2 border-gray-200/50 dark:border-gray-600/50 rounded-xl focus:outline-none focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 dark:focus:border-blue-400 backdrop-blur-sm transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400',
                'placeholder': 'Enter a descriptive name for your device'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input w-full px-4 py-4 bg-white/70 dark:bg-black/30 border-2 border-gray-200/50 dark:border-gray-600/50 rounded-xl focus:outline-none focus:ring-4 focus:ring-green-500/20 focus:border-green-500 dark:focus:border-green-400 backdrop-blur-sm transition-all duration-200 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400',
                'placeholder': 'e.g., Kitchen Counter, Living Room Corner'
            }),
            'room': forms.Select(attrs={
                'class': 'form-input w-full px-4 py-4 bg-white/70 dark:bg-black/30 border-2 border-gray-200/50 dark:border-gray-600/50 rounded-xl focus:outline-none focus:ring-4 focus:ring-purple-500/20 focus:border-purple-500 dark:focus:border-purple-400 backdrop-blur-sm transition-all duration-200 text-gray-900 dark:text-white appearance-none cursor-pointer'
            }),
            'user': forms.Select(attrs={
                'class': 'form-input w-full px-4 py-4 bg-white/70 dark:bg-black/30 border-2 border-gray-200/50 dark:border-gray-600/50 rounded-xl focus:outline-none focus:ring-4 focus:ring-orange-500/20 focus:border-orange-500 dark:focus:border-orange-400 backdrop-blur-sm transition-all duration-200 text-gray-900 dark:text-white appearance-none cursor-pointer'
            }),
            'device_type': forms.Select(attrs={
                'class': 'form-input w-full px-4 py-4 bg-white/70 dark:bg-black/30 border-2 border-gray-200/50 dark:border-gray-600/50 rounded-xl focus:outline-none focus:ring-4 focus:ring-indigo-500/20 focus:border-indigo-500 dark:focus:border-indigo-400 backdrop-blur-sm transition-all duration-200 text-gray-900 dark:text-white appearance-none cursor-pointer'
            }),
            'status': forms.CheckboxInput(attrs={
                'class': 'sr-only peer', # Tailwind class to visually hide but keep accessible
                'id': 'id_status' # Ensure the ID matches for the label 'for' attribute
            }),
        }
    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError("Device name must be at least 3 characters!")
        return name