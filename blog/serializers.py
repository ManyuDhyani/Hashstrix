from rest_framework import serializers
from .models import Post, Author
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'username']
        
class AuthorSerializer(serializers.ModelSerializer):
    user = AuthUserSerializer(read_only=True)
    class Meta:
        model = Author
        fields = ['id', 'profile_picture', 'verified', 'user']

class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['id', 'title', 'overview', 'timestamp', 'content', 'thumbnail', 'category', 'author']

class TraveloftindiaPostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ['title', 'overview', 'timestamp', 'thumbnail', 'author', 'slug']