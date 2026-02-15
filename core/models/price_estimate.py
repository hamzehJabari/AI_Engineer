from django.db import models


class PriceEstimate(models.Model):
    """A price estimation result for a car."""

    CATEGORY_CHOICES = [
        ('luxury', 'Luxury'),
        ('premium', 'Premium'),
        ('economic', 'Economic'),
    ]

    make = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    mileage_km = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    original_price_jod = models.DecimalField(max_digits=10, decimal_places=2)
    depreciated_price_jod = models.DecimalField(max_digits=10, decimal_places=2)
    depreciation_pct = models.DecimalField(max_digits=5, decimal_places=2)
    breakdown = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Estimate: {self.year} {self.make} {self.model} → {self.depreciated_price_jod} JOD"
