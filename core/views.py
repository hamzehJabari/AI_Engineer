from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def home(request):
    """Landing page for IntelliWheels."""
    return render(request, 'core/home.html')


@require_GET
def health_check(request):
    """Health check endpoint."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'IntelliWheels Car Marketplace AI',
        'version': '1.0.0',
    })
