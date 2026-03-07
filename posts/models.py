from django.db import models

from creators.models import Creator


class Post(models.Model):
    """Публикации автора"""

    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    body = models.TextField
    is_paid = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
