"""
Chat API view - handles the IntelliWheels chatbot conversation.
"""
import time
import logging

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers as drf_serializers

from core.models.chat import ChatSession, ChatMessage
from core.serializers.chat_serializers import ChatInputSerializer
from ai_engine.agents.car_chatbot import CarChatbotAgent

logger = logging.getLogger(__name__)


class ChatView(APIView):
    """POST /api/chat/ - send a message, get an AI reply."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Chat'],
        summary='Send a message to the AI chatbot',
        description='Send a user message and receive an AI-generated response about cars and the Jordanian market.',
        request=ChatInputSerializer,
        responses={200: inline_serializer(
            name='ChatResponse',
            fields={
                'message': drf_serializers.CharField(),
                'session_id': drf_serializers.IntegerField(),
                'model_used': drf_serializers.CharField(),
                'response_time_ms': drf_serializers.IntegerField(),
            }
        )},
    )
    def post(self, request):
        serializer = ChatInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Get or create session
        session_id = data.get('session_id')
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id)
            except ChatSession.DoesNotExist:
                session = ChatSession.objects.create()
        else:
            session = ChatSession.objects.create()

        # Save user message
        ChatMessage.objects.create(
            session=session, role='user', content=data['message']
        )

        # Build history
        history = list(
            session.messages.order_by('created_at').values('role', 'content')
        )

        # AI response
        start = time.time()
        try:
            agent = CarChatbotAgent()
            result = agent.chat(data['message'], history=history[:-1])
            ai_text = result['response']
            model_used = result.get('model_used', '')
        except Exception as e:
            logger.error(f"Chat AI error: {e}")
            ai_text = "Sorry, I couldn't process your request right now. Please try again."
            model_used = "error"

        elapsed_ms = int((time.time() - start) * 1000)

        # Save assistant message
        ChatMessage.objects.create(
            session=session, role='assistant', content=ai_text
        )

        return Response({
            'message': ai_text,
            'session_id': session.id,
            'model_used': model_used,
            'response_time_ms': elapsed_ms,
        })
