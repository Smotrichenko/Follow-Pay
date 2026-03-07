from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "creator", "title", "body", "is_paid", "is_published", "created_at", "published_at")
        read_only_fields = ("id", "creator", "is_published", "created_at", "published_at")
