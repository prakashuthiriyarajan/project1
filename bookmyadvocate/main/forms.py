"""
Path: bookmyadvocate/main/forms.py
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, AdvocateProfile, Booking

class ClientSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email','password1','password2')
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role='client'; user.is_active=True
        if commit: user.save()
        return user

class AdvocateSignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username','email','password1','password2')
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role='advocate'; user.is_active=False; user.is_active_advocate=False
        if commit: user.save()
        return user

class AdvocateProfileForm(forms.ModelForm):
    class Meta:
        model = AdvocateProfile
        fields = ['specialization','experience_years','location','bio']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date','time','purpose']
