from django.contrib import admin
from django.urls import path, include
from .views import Login,accounts,log_out
urlpatterns = [
    path('accounts/login/', Login.as_view(), name='login'),
    path('accounts/', accounts, name='accounts'),
    path('accounts/logout/', log_out, name='logout'),

]