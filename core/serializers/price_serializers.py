from rest_framework import serializers
from core.models.price_estimate import PriceEstimate


class PriceEstimateInputSerializer(serializers.Serializer):
    """Input for the price estimator endpoint."""
    make = serializers.CharField(max_length=50)
    model = serializers.CharField(max_length=100)
    year = serializers.IntegerField(min_value=1980, max_value=2026)
    mileage_km = serializers.IntegerField(min_value=0, default=0)


class PriceEstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceEstimate
        fields = [
            'id', 'make', 'model', 'year', 'mileage_km',
            'category', 'original_price_jod', 'depreciated_price_jod',
            'depreciation_pct', 'breakdown', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
