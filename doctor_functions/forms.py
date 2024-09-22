# doctor_functions/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfileModel

class UserProfileForm(UserCreationForm):
    name = forms.CharField(max_length=120)
    speciality = forms.CharField(max_length=120)
    picture = forms.ImageField(required=False)
    details = forms.CharField(widget=forms.Textarea)
    experience = forms.CharField(widget=forms.Textarea)
    twitter = forms.CharField(max_length=120, required=False)
    facebook = forms.CharField(max_length=120, required=False)
    instagram = forms.CharField(max_length=120, required=False)

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'name', 'speciality', 'picture', 'details', 'experience', 'twitter', 'facebook', 'instagram')
