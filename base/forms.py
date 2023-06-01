from django.forms import ModelForm
from .models import Room, User, Application

from django.contrib.auth.forms import UserCreationForm 
from django import forms


class RoomForm(ModelForm):
    class Meta:
        model = Room
        # fields = '__all__' if you want to include all fields in the form
        fields = '__all__' 
        exclude = ['recruiter']


class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2'] #1 and 2 for password confirmation

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['avatar', 'name', 'username', 'email', 'linkedin', 'bio']

class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ['resume', 'experience']





