from rest_framework import serializers
from core.models.vision_analysis import VisionAnalysis


class VisionAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisionAnalysis
        fields = [
            'id', 'image', 'detected_make', 'detected_model',
            'detected_year', 'condition_summary', 'created_at',
        ]
        read_only_fields = ['id', 'detected_make', 'detected_model',
                            'detected_year', 'condition_summary', 'created_at']
