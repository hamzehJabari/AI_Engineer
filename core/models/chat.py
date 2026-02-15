from django.db import models


class ChatSession(models.Model):
    """A chat conversation session."""

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    summary = models.TextField(blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Session #{self.pk} ({self.started_at:%Y-%m-%d %H:%M})"


class ChatMessage(models.Model):
    """A single message in a chat session."""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        preview = self.content[:60] + '...' if len(self.content) > 60 else self.content
        return f"[{self.role}] {preview}"
