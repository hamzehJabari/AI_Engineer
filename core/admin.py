from django.contrib import admin
from core.models import CarListing, ChatSession, ChatMessage, PriceEstimate, VisionAnalysis


@admin.register(CarListing)
class CarListingAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'category', 'listing_price_jod', 'is_sold')
    list_filter = ('category', 'make', 'is_sold')
    search_fields = ('make', 'model')


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'started_at', 'ended_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'created_at')
    list_filter = ('role',)


@admin.register(PriceEstimate)
class PriceEstimateAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'category', 'depreciated_price_jod', 'created_at')
    list_filter = ('category',)


@admin.register(VisionAnalysis)
class VisionAnalysisAdmin(admin.ModelAdmin):
    list_display = ('detected_make', 'detected_model', 'detected_year', 'created_at')
