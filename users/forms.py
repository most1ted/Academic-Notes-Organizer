from django.forms import forms
from django import forms
from django.contrib.auth.models import User
from .models import User, Course
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Note
User = get_user_model()
class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Password'}))

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

class RegisterForm(forms.Form):
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

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered")
        return email

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content','file','is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Content'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'placeholder': 'File'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),



        }
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title','description','code','is_public','price'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description'}),
            'code' :forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),

        }
        def clean_title(self):
            title =self.cleaned_data.get('title')
            if len(title) <3:
                raise forms.ValidationError("Please enter your title.")
            return title


