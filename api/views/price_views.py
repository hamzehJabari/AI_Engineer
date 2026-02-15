"""
Price Estimator API view - crisp logic car valuation.
"""
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers

from core.serializers.price_serializers import PriceEstimateInputSerializer
from core.models.price_estimate import PriceEstimate
from ai_engine.price_estimator import estimate_price, get_all_makes, get_models_for_make

logger = logging.getLogger(__name__)


class PriceEstimateView(APIView):
    """POST /api/estimate/ - estimate a car price."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Price Estimator'],
        summary='Estimate a car price',
        description='Get a rule-based price estimate for a car in JOD, including depreciation and category classification.',
        request=PriceEstimateInputSerializer,
        responses={200: inline_serializer(
            name='PriceEstimateResponse',
            fields={
                'make': drf_serializers.CharField(),
                'model': drf_serializers.CharField(),
                'year': drf_serializers.IntegerField(),
                'mileage_km': drf_serializers.IntegerField(),
                'category': drf_serializers.CharField(),
                'original_price_jod': drf_serializers.FloatField(),
                'depreciated_price_jod': drf_serializers.FloatField(),
                'depreciation_pct': drf_serializers.FloatField(),
                'breakdown': drf_serializers.DictField(),
            }
        )},
    )
    def post(self, request):
        serializer = PriceEstimateInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        result = estimate_price(
            make=data["make"],
            model=data["model"],
            year=data["year"],
            mileage_km=data.get("mileage_km", 0),
        )

        # Persist
        PriceEstimate.objects.create(
            make=result["make"],
            model=result["model"],
            year=result["year"],
            mileage_km=result["mileage_km"],
            category=result["category"],
            original_price_jod=result["original_price_jod"],
            depreciated_price_jod=result["depreciated_price_jod"],
            depreciation_pct=result["depreciation_pct"],
            breakdown=result["breakdown"],
        )

        return Response(result)


class CarMakesView(APIView):
    """GET /api/makes/ - list all known car makes."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Price Estimator'],
        summary='List all car makes',
        description='Returns a list of all known car makes supported by the price estimator.',
        responses={200: inline_serializer(
            name='CarMakesResponse',
            fields={'makes': drf_serializers.ListField(child=drf_serializers.CharField())}
        )},
    )
    def get(self, request):
        return Response({"makes": get_all_makes()})


class CarModelsView(APIView):
    """GET /api/models/<make>/ - list models for a make."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Price Estimator'],
        summary='List models for a car make',
        description='Returns a list of all known models for a given car make.',
        responses={200: inline_serializer(
            name='CarModelsResponse',
            fields={
                'make': drf_serializers.CharField(),
                'models': drf_serializers.ListField(child=drf_serializers.CharField()),
            }
        )},
    )
    def get(self, request, make):
        models = get_models_for_make(make)
        return Response({"make": make, "models": models})
