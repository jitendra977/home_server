from django import forms
from .models import Appliance, Room
from django.contrib.auth import get_user_model

User = get_user_model()

class ApplianceForm(forms.ModelForm):
    class Meta:
        model = Appliance
        fields = ['name', 'location', 'room', 'user', 'device_type', 'status', 'is_active']
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
                'class': 'sr-only peer',
                'id': 'id_status'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'sr-only peer',
                'id': 'id_is_active'
            }),
        }
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter rooms based on ownership
        if self.user:
            if not self.user.is_superuser:
                self.fields['room'].queryset = Room.objects.filter(owner=self.user)
            else:
                self.fields['room'].queryset = Room.objects.all()
        
        # Handle user assignment
        if 'user' in self.fields:
            if not self.user.is_superuser:
                # Regular users can only assign to themselves
                self.fields['user'].queryset = User.objects.filter(pk=self.user.pk)
                self.fields['user'].initial = self.user
                self.fields['user'].widget.attrs['disabled'] = True
            else:
                # Superusers can assign to any active user
                self.fields['user'].queryset = User.objects.filter(is_active=True)
        
        # Set defaults for new devices
        if not self.instance.pk:
            self.fields['status'].initial = False
            self.fields['is_active'].initial = True
            if self.user and not self.user.is_superuser:
                self.fields['user'].initial = self.user

    def clean(self):
        cleaned_data = super().clean()
        
        if self.user and not self.user.is_superuser:
            # Validate room ownership
            room = cleaned_data.get('room')
            if room and room.owner != self.user:
                raise forms.ValidationError("You can only assign devices to your own rooms.")
            
            # Validate user assignment
            user = cleaned_data.get('user')
            if user and user != self.user:
                raise forms.ValidationError("You can only assign devices to yourself.")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Ensure regular users can't override assignment
        if self.user and not self.user.is_superuser:
            instance.user = self.user
        
        if commit:
            instance.save()
        
        return instance