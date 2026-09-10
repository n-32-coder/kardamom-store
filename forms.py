from django import forms

from .models import Customer


class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'date_of_birth']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
