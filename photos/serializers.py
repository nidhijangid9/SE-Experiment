from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Photo, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'created_at', 'user', 'photo')
        read_only_fields = ('user', 'photo')

class PhotoSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.CharField(write_only=True, required=False)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Photo
        fields = ('id', 'name', 'image', 'description', 'category', 
                 'category_id', 'user', 'created', 'last_updated', 'comments')
