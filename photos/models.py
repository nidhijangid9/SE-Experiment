from django.db import models
from uuid import uuid4

# Create your models here.


class Category(models.Model):
    id = models.CharField(
        max_length=225,
        unique=True,
        blank=False,
        null=False,
        default=uuid4,
        primary_key=True)
    name = models.CharField(max_length=100, null=False,
                            blank=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


from django.contrib.auth.models import User

class Photo(models.Model):
    id = models.CharField(
        max_length=225,
        unique=True,
        blank=False,
        null=False,
        default=uuid4,
        primary_key=True)
    name = models.CharField(max_length=100, null=False,
                            blank=False)
    image = models.ImageField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True)  # New field
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description

    id = models.CharField(
        max_length=225,
        unique=True,
        blank=False,
        null=False,
        default=uuid4,
        primary_key=True)
    name = models.CharField(max_length=100, null=False,
                            blank=False)
    image = models.ImageField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description

from django.db import models
from django.contrib.auth.models import User
from .models import Photo

class Comment(models.Model):
    photo = models.ForeignKey(Photo, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.photo.name}"
