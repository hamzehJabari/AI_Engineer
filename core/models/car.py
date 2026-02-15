from django.db import models


class CarListing(models.Model):
    """A car listing in the IntelliWheels marketplace."""

    CATEGORY_CHOICES = [
        ('luxury', 'Luxury'),
        ('premium', 'Premium'),
        ('economic', 'Economic'),
    ]

    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('hybrid', 'Hybrid'),
        ('electric', 'Electric'),
    ]

    TRANSMISSION_CHOICES = [
        ('automatic', 'Automatic'),
        ('manual', 'Manual'),
    ]

    make = models.CharField(max_length=50)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    mileage_km = models.PositiveIntegerField(default=0)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='petrol')
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='automatic')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True)
    color = models.CharField(max_length=30, blank=True)
    original_price_jod = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    listing_price_jod = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Car Listing'
        verbose_name_plural = 'Car Listings'

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"
