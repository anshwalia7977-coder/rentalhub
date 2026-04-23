from django import forms
from .models import UserInfo
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):

    class Meta:
        model = UserInfo
        fields = ['name', 'age', 'gender', 'phone_number', 'address', 'email', 'username', 'password1', 'password2']
        widgets = {
            'password': forms.PasswordInput(),
        }

from django import forms
from .models import UserInfo
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')    

    

class EditProfileForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        fields = ['name', 'age', 'gender', 'phone_number', 'address', 'email']
        

