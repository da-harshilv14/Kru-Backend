from django.db import models

class Subsidy(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    eligibility = models.JSONField(default=list, blank=True)
    documents_required = models.JSONField(default=list, blank=True)
    application_start_date = models.DateField(blank=True, null=True)
    application_end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Subsidies"
