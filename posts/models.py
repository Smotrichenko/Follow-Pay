from django.db import models

from creators.models import Creator


class Post(models.Model):
    """Публикации автора"""

    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, related_name="posts", verbose_name="Автор поста")
    title = models.CharField(max_length=200, verbose_name="Заголовок поста")
    body = models.TextField(verbose_name="Тело поста")
    is_paid = models.BooleanField(default=False, verbose_name="Доступ подписчикам")
    is_published = models.BooleanField(default=False, verbose_name="Публикация поста")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания поста")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата опубликования поста")

    def __str__(self):
        return self.title
