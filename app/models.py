from django.conf import settings
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Subsidy(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    eligibility = models.JSONField(default=list, blank=True)
    documents_required = models.JSONField(default=list, blank=True)
    application_start_date = models.DateField(blank=True, null=True)
    application_end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_subsidies', help_text='User who created this subsidy (subsidy_provider)')
    rating = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)], help_text="Average rating from 0 to 5 stars")

    def update_average_rating(self):
        """Recalculate and store the average rating for this subsidy."""
        avg = self.ratings.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        self.rating = round(avg or 0.0, 1)
        self.save(update_fields=["rating"])

    def __str__(self):
        return f"{self.title} ({self.rating}⭐)"

    class Meta:
        verbose_name_plural = "Subsidies"


class SubsidyRating(models.Model):
    subsidy = models.ForeignKey(Subsidy, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subsidy_ratings')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], help_text="Rate this subsidy from 1 (poor) to 5 (excellent)")
    review = models.TextField(blank=True, help_text="Optional review about the subsidy")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subsidy', 'user') # one rating per user
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} rated {self.subsidy} {self.rating}/5"

    def save(self, *args, **kwargs):
        """Update subsidy average rating when saved."""
        super().save(*args, **kwargs)
        self.subsidy.update_average_rating()

    def delete(self, *args, **kwargs):
        """Update subsidy average rating when deleted."""
        super().delete(*args, **kwargs)
        self.subsidy.update_average_rating()
