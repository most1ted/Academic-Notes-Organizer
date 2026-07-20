from django.contrib import admin
from django.urls import path, include

from . import views
urlpatterns = [
    path('accounts/login/', views.Login.as_view(), name='login'),
    path('accounts/', views.accounts, name='accounts'),
    path('accounts/logout/', views.log_out, name='logout'),
    path('courses/', views.course_list, name='courses'),
    path('courses/create/',views.course_create, name='course_create'),
    path('courses/<int:course_id>/',views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/',views.course_edit, name='course_edit'),
    path('courses/<int:course_id>/delete/',views.course_delete, name='course_delete'),


]