"""
Vision Helper API view - analyze car images with Gemini Vision.
"""
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiRequest
from rest_framework import serializers as drf_serializers

from core.models.vision_analysis import VisionAnalysis
from ai_engine.vision_helper import analyze_car_image

logger = logging.getLogger(__name__)


class VisionAnalyzeView(APIView):
    """POST /api/vision/ - upload a car image for AI analysis."""

    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        tags=['Vision'],
        summary='Analyze a car image',
        description='Upload a car photo (JPEG, PNG, WebP, GIF) and Gemini Vision will identify the make, model, year, and condition.',
        request=inline_serializer(
            name='VisionUploadRequest',
            fields={'image': drf_serializers.ImageField()}
        ),
        responses={200: inline_serializer(
            name='VisionAnalysisResponse',
            fields={
                'id': drf_serializers.IntegerField(),
                'make': drf_serializers.CharField(),
                'model': drf_serializers.CharField(),
                'year': drf_serializers.CharField(),
                'condition': drf_serializers.CharField(),
            }
        )},
    )
    def post(self, request):
        image_file = request.FILES.get("image")
        if not image_file:
            return Response(
                {"error": "No image file provided. Send as 'image' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate basic file type
        allowed = ["image/jpeg", "image/png", "image/webp", "image/gif"]
        if image_file.content_type not in allowed:
            return Response(
                {"error": f"Unsupported image type: {image_file.content_type}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            image_bytes = image_file.read()
            result = analyze_car_image(image_bytes)

            # Persist
            image_file.seek(0)
            analysis = VisionAnalysis.objects.create(
                image=image_file,
                detected_make=result.get("make", ""),
                detected_model=result.get("model", ""),
                detected_year=result.get("year", ""),
                condition_summary=result.get("condition", ""),
                raw_response=result.get("raw_response", ""),
            )

            return Response({
                "id": analysis.id,
                "make": analysis.detected_make,
                "model": analysis.detected_model,
                "year": analysis.detected_year,
                "condition": analysis.condition_summary,
            })

        except Exception as e:
            logger.error(f"Vision analysis error: {e}")
            return Response(
                {"error": f"Failed to analyze image: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
