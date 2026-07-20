from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import os
from django.core.validators import FileExtensionValidator,MaxValueValidator


class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    count = models.IntegerField(default=0,null=True,blank=True)
    profile_pic = models.ImageField(upload_to='users/',blank=True)
    def __str__(self):
        return self.username
class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    code = models.IntegerField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    price =models.DecimalField(max_digits=10,decimal_places=2,default=0)
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    class Meta:
        ordering = ['-created_at']
    def fet_notes_count(self):
        return self.notes.count()
    def get_last_note(self):
        return self.notes.order_by('-created_at').first()
class Note(models.Model):
    course = models.ForeignKey(Course,on_delete=models.CASCADE ,related_name='notes')
    title = models.CharField(max_length=100)
    content = models.TextField()
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    content = models.TextField()
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    file = models.FileField(upload_to='notes/',blank=True)
    class Meta:
        ordering = ['-created_at']
    is_public = models.BooleanField(default=True)
    views_count = models.IntegerField(default=0)
    class Meta:
        ordering = ['-created_at']
    file = models.FileField(
        upload_to='notes/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf','png','jpg','jpeg','gif','doc','docx','txt','md'])])

    original_filename = models.CharField(blank=True,max_length=100)
    file_size = models.PositiveIntegerField(default=0)
    file_type= models.CharField(blank=True,max_length=100)
    def save(self, *args, **kwargs):
        if self.file:
            self.original_filename = self.file.name.split('/')[-1]
            self.file_size = self.file.size
            ext = os.path.splitext(self.file.name)[1].lower()
            self.file_type = ext[1:] if ext else 'unknown'
        super().save(*args, **kwargs)

    def get_file_icon(self):
        icons = {
            'pdf': 'fa-file-pdf',
            'doc': 'fa-file-word',
            'docx': 'fa-file-word',
            'txt': 'fa-file-alt',
            'md': 'fa-file-alt',
            'jpg': 'fa-file-image',
            'jpeg': 'fa-file-image',
            'png': 'fa-file-image',
        }
        return icons.get(self.file_type ,'fa-file')

