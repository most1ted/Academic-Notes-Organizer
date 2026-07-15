from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from users.forms import LoginForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm,LoginForm
from django.contrib import messages
from django.contrib.auth import get_user_model

@login_required
def accounts(request):
    return render(request,'base.html')
def log_out(request):
    logout(request)
    return redirect('login')

User = get_user_model()

class Login(AccessMixin, View):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('accounts')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)

        login_form = LoginForm()
        register_form = RegisterForm()

        return render(request, self.template_name, {
            'login_form': login_form,
            'register_form': register_form
        })

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)

        if 'login_submit' in request.POST:
            login_form = LoginForm(request.POST)
            register_form = RegisterForm()

            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return HttpResponseRedirect(self.success_url)

            return render(request, self.template_name, {
                'login_form': login_form,
                'register_form': register_form
            })

        elif 'register_submit' in request.POST:
            register_form = RegisterForm(request.POST)
            login_form = LoginForm()

            if register_form.is_valid():
                username = register_form.cleaned_data['username']
                email = register_form.cleaned_data['email']
                password = register_form.cleaned_data['password']


                new_user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                new_user.save()

                login(request, new_user)
                return redirect('accounts')



            return render(request, self.template_name, {
                'login_form': login_form,
                'register_form': register_form
            })

        return HttpResponseRedirect(self.success_url)

