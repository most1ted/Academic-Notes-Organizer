from django.contrib.auth.models import User
from .models import User
from django.contrib.auth import authenticate

from django.contrib.auth import get_user_model

from django import forms
from .models import Note, Course
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
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if data is None:
            return []

        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data]

        return [single_file_clean(data, initial)]
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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={
            'class': 'd-none',
            'id': 'fileInput',
            'multiple': True,
            'name': 'files',

        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            return [single_file_clean(d, initial) for d in data if d]
        return [single_file_clean(data, initial)] if data else []
class NoteForm(forms.ModelForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select rounded-pill shadow-sm',
            'style': 'padding: 12px 20px; font-size: 16px; border: 2px solid #e0e0e0;',
            'required': 'required'
        }),
        label="Select Course",
        empty_label=" Choose a course..."
    )


    files = MultipleFileField(
        required=False,
        label="Attach Files",


    )

    class Meta:
        model = Note
        fields = ['course', 'title', 'content', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control rounded-3 shadow-sm',
                'style': 'padding: 12px 16px; font-size: 16px; border: 2px solid #e0e0e0;',
                'placeholder': ' Enter note title...'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control rounded-3 shadow-sm',
                'style': 'padding: 12px 16px; font-size: 16px; border: 2px solid #e0e0e0; min-height: 200px;',
                'rows': 10,
                'placeholder': ' Write your note content here...'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'style': 'width: 20px; height: 20px; cursor: pointer;'
            }),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)

        super().__init__(*args, **kwargs)
        if request and hasattr(request, 'user') and request.user.is_authenticated:

            self.fields['course'].queryset = Course.objects.filter(user=request.user)


            print(f"🔵 User: {request.user.username}, Courses count: {Course.objects.filter(user=request.user).count()}")
            for course in Course.objects.filter(user=request.user):
                print(f"   - Course: {course.title} (ID: {course.id})")
        else:
            print("❌ No request or user not authenticated")
        if self.instance and self.instance.pk and self.instance.course:
            self.fields['course'].initial = self.instance.course
