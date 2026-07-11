from django.forms import forms
from django import forms
from django.contrib.auth.models import User
from .models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("username or password is incorrect")

            self._user = user
        return cleaned_data

    def get_user(self):

        return getattr(self, '_user', None)

class RegisterForms(forms.Form):
    fields = ['username', 'email', 'password']
    username = forms.CharField(label='Username', max_length=100,
                               error_messages={
                                   'required': 'Please enter your username.'}
                               , widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    email = forms.EmailField(label='Email', max_length=100, required=True, error_messages={
        'required': 'Please enter your email.',
    },widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(label='Password', max_length=100, required=True, error_messages={
        'required': 'Please enter your password.',
    }, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name in self.fields:
            field = self.fields[name]
            field.widget.attrs.update({
                'onfocus': f'animateField(this)',
                'onblur': f'revertAnimation(this)'
            })

    def clean_numbers(self):
        numbers = self.cleaned_data.get('numbers')
        if not numbers.isdigit():
            raise forms.ValidationError("Please enter valid numbers.")
        return numbers

class LogintForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Username or password is incorrect")
            self._user = user
        return cleaned_data

    def get_user(self):
        return getattr(self, '_user', None)

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username'
        })
    )
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already registered")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already registered")
        return email