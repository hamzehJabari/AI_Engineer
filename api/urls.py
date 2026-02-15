from django.urls import path
from api.views import chat_views, price_views, vision_views, whatsapp_views

app_name = 'api'

urlpatterns = [
    # Chat
    path('chat/', chat_views.ChatView.as_view(), name='chat'),

    # Price Estimator
    path('estimate/', price_views.PriceEstimateView.as_view(), name='estimate'),
    path('makes/', price_views.CarMakesView.as_view(), name='makes'),
    path('models/<str:make>/', price_views.CarModelsView.as_view(), name='models'),

    # Vision Helper
    path('vision/', vision_views.VisionAnalyzeView.as_view(), name='vision'),

    # WhatsApp
    path('whatsapp/send/', whatsapp_views.WhatsAppSendView.as_view(), name='whatsapp_send'),
]
