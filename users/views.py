from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View



class RegisterView(View):

    def get(self, request):
        register_form = RegisterForm()
        context = {
            'register_form': register_form
        }
        return render(request, 'register.html', context)

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_email = register_form.cleaned_data['email']
            user_password = register_form.cleaned_data['password']

            user_name = register_form.cleaned_data['username']
            double: bool = User.objects.filter(email=user_email).exists()
            three: bool = User.objects.filter(username=user_name).exists()
            if double:
                register_form.errors['email'] = ("Email already registered")
            if three:
                register_form.errors['username'] = ("Username already registered")
            else:
                new_user = User(
                    email=user_email,
                    numbers=user_number,
                    username=user_name,
                    num=random.randint(10 ** 15, 10 ** 16 - 1),
                    value=user_value,
                    is_active=True
                )
                new_user.set_password(user_password)
                new_user.save()
                return redirect('main')

        context = {
            'register_form': register_form
        }
        return render(request, 'register.html', context)


