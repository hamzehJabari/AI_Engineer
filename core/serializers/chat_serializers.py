from rest_framework import serializers
from core.models.chat import ChatSession, ChatMessage


class ChatInputSerializer(serializers.Serializer):
    """Input for the chat endpoint."""
    message = serializers.CharField(max_length=5000)
    session_id = serializers.IntegerField(required=False, allow_null=True)


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)

    class Meta:
        model = ChatSession
        fields = ['id', 'started_at', 'ended_at', 'summary', 'messages']
