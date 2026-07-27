from django.contrib import admin
from django.urls import path, include

from . import views
urlpatterns = [
    path('accounts/login/', views.Login.as_view(), name='login'),

    path('accounts/logout/', views.log_out, name='logout'),
    path('courses/', views.course_list, name='courses'),
    path('courses/create/',views.course_create, name='course_create'),
    path('courses/<int:course_id>/',views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/edit/',views.course_edit, name='course_edit'),
    path('courses/<int:course_id>/delete/',views.course_delete, name='course_delete'),
path('notes/', views.note_list, name='note_list'),
    path('notes/create/', views.note_create, name='note_create'),
    path('notes/<int:note_id>/edit/', views.note_edit, name='note_edit'),
    path('notes/<int:note_id>/delete/', views.note_delete, name='note_delete'),
    path('note/download/<int:file_id>/', views.note_download, name='note_download'),
    path('note/delete-file/<int:file_id>/', views.note_delete_file, name='note_delete_file'),
    path('note/<int:note_id>/', views.note_detail, name='note_detail'),
    path('', views.main, name='main'),


]