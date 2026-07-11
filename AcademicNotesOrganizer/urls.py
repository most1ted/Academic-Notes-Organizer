from django.contrib import admin
from django.urls import path
from django.urls import include
from .views import main

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main, name='main'),

    path('', include('users.urls')),
]
