from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    creator_display_name = serializers.CharField(source="creator.display_name", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "creator",
            "creator_display_name",
            "title",
            "body",
            "is_paid",
            "is_published",
            "created_at",
            "published_at",
        )
        read_only_fields = ("id", "creator", "creator_display_name", "is_published", "created_at", "published_at")
