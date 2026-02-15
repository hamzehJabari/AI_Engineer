"""
WhatsApp API view - send messages via Twilio WhatsApp.
"""
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers

from django.conf import settings
from core.tools.whatsapp_twilio import send_whatsapp_message

logger = logging.getLogger(__name__)


class WhatsAppSendView(APIView):
    """POST /api/whatsapp/send/ - send a message via WhatsApp."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['WhatsApp'],
        summary='Send a WhatsApp message',
        description='Send a message via Twilio WhatsApp. If no recipient is specified, uses the default from settings.',
        request=inline_serializer(
            name='WhatsAppSendRequest',
            fields={
                'message': drf_serializers.CharField(),
                'to': drf_serializers.CharField(required=False),
            }
        ),
        responses={200: inline_serializer(
            name='WhatsAppSendResponse',
            fields={
                'status': drf_serializers.CharField(),
                'sid': drf_serializers.CharField(),
                'to': drf_serializers.CharField(),
            }
        )},
    )
    def post(self, request):
        text = request.data.get("message", "").strip()
        to = request.data.get("to", "").strip()

        if not text:
            return Response(
                {"error": "message is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Use provided 'to' or fall back to settings default
        if not to:
            to = getattr(settings, 'TWILIO_WHATSAPP_TO', '')
        if not to:
            return Response(
                {"error": "No recipient. Provide 'to' or set TWILIO_WHATSAPP_TO in .env"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            sid = send_whatsapp_message(to=to, text=text)
            return Response({
                "status": "sent",
                "sid": sid,
                "to": to,
            })
        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
