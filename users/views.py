from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin
from users.forms import LoginForm
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm,LoginForm
class Login(View):

    def get(self, request):
        form = LoginForm()
        context = {
            'form': form
        }
        return render(request, 'login.html', context)

    def post(self, request):
        register_form = LoginForm(request.POST)
        if register_form.is_valid():
            user_name = register_form.cleaned_data['username']
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
                    username=user_name,
                )
                new_user.set_password(user_password)
                new_user.save()
                return redirect('main')

        context = {
            'register_form': register_form
        }
        return render(request, 'login.html', context)
class LogintView(AccessMixin, View):
    template_name = 'login.html'
    form_class = LoginForm

    success_url = reverse_lazy('main')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)

        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect(self.success_url)

        return render(request, self.template_name, {'form': form})


# class LoginView(AccessMixin, View):
#     template_name = 'login.html'
#     form_class = LoginForm
#     success_url = reverse_lazy('main')
#
#     def get(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             return HttpResponseRedirect(self.success_url)
#
#         # هر دو فرم را آماده کنید
#         login_form = LoginForm()
#         register_form = RegisterForm()
#
#         return render(request, self.template_name, {
#             'login_form': login_form,  # فرم ورود
#             'register_form': register_form  # فرم ثبت‌نام
#         })
#
#     def post(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             return HttpResponseRedirect(self.success_url)
#
#         # تشخیص اینکه کدام فرم ارسال شده
#         if 'login_submit' in request.POST:
#             # فرم ورود
#             login_form = LoginForm(request.POST)
#             register_form = RegisterForm()  # فرم ثبت‌نام خالی برای نمایش
#
#             if login_form.is_valid():
#                 user = login_form.get_user()
#                 login(request, user)
#                 return HttpResponseRedirect(self.success_url)
#
#             return render(request, self.template_name, {
#                 'login_form': login_form,
#                 'register_form': register_form
#             })
#
#         elif 'register_submit' in request.POST:
#             # فرم ثبت‌نام
#             register_form = RegisterForm(request.POST)
#             login_form = LoginForm()  # فرم ورود خالی برای نمایش
#
#             if register_form.is_valid():
#                 username = register_form.cleaned_data['username']
#                 email = register_form.cleaned_data['email']
#                 password = register_form.cleaned_data['password']
#
#                 # ایجاد کاربر جدید
#                 new_user = User.objects.create_user(
#                     username=username,
#                     email=email,
#                     password=password
#                 )
#                 new_user.save()
#
#                 # لاگین خودکار بعد از ثبت‌نام
#                 login(request, new_user)
#                 return redirect('main')
#
#             return render(request, self.template_name, {
#                 'login_form': login_form,
#                 'register_form': register_form
#             })
#
#         # اگر هیچکدام نبود
#         return HttpResponseRedirect(self.success_url)
class LoginView(AccessMixin, View):
    template_name = 'login.html'
    form_class = LoginForm

    success_url = reverse_lazy('main')

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)


        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)

        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return HttpResponseRedirect(self.success_url)

        return render(request, self.template_name, {'form': form})


