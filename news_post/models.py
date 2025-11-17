from django.db import models
from cloudinary.models import CloudinaryField
from django.conf import settings

class Article(models.Model):
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="articles"
    )

    title = models.CharField(max_length=255)
    date = models.DateField()
    tag = models.CharField(max_length=50, default="General")
    source = models.CharField(max_length=255)  # e.g., Government of India
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.provider.full_name})"
