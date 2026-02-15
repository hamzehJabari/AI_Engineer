from django.db import models


def car_image_upload_path(instance, filename):
    return f'car_images/{filename}'


class VisionAnalysis(models.Model):
    """Result of an AI vision analysis on a car image."""

    image = models.ImageField(upload_to=car_image_upload_path)
    detected_make = models.CharField(max_length=50, blank=True)
    detected_model = models.CharField(max_length=100, blank=True)
    detected_year = models.CharField(max_length=20, blank=True)
    condition_summary = models.TextField(blank=True)
    raw_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Vision Analysis'
        verbose_name_plural = 'Vision Analyses'

    def __str__(self):
        return f"Vision: {self.detected_make} {self.detected_model} ({self.detected_year})"
