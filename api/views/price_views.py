"""
Price Estimator API view - crisp logic car valuation.
"""
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from core.serializers.price_serializers import PriceEstimateInputSerializer
from core.models.price_estimate import PriceEstimate
from ai_engine.price_estimator import estimate_price, get_all_makes, get_models_for_make

logger = logging.getLogger(__name__)


class PriceEstimateView(APIView):
    """POST /api/estimate/ - estimate a car price."""

    permission_classes = [AllowAny]

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

    def get(self, request):
        return Response({"makes": get_all_makes()})


class CarModelsView(APIView):
    """GET /api/models/<make>/ - list models for a make."""

    permission_classes = [AllowAny]

    def get(self, request, make):
        models = get_models_for_make(make)
        return Response({"make": make, "models": models})
