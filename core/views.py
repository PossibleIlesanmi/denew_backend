from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Create your views here.

def home(request):
    """Render the home page"""
    return render(request, 'index.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """API root endpoint that returns available endpoints"""
    return Response({
        'status': 'success',
        'message': 'Welcome to Denew Networking API',
        'version': '1.0.0',
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring"""
    return Response({
        'status': 'healthy',
        'message': 'System is running normally',
    })
