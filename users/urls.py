from django.contrib import admin
from django.urls import path, include
from .views import Login
urlpatterns = [
    path('accounts/login/', Login.as_view(), name='login'),

]