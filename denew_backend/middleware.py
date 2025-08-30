from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import time

class OperatingHoursMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_time = timezone.now().time()
        if not (time(9, 0) <= current_time <= time(21, 59)):
            return Response({'error': 'Platform is closed outside 9:00-21:59'}, status=status.HTTP_403_FORBIDDEN)
        return self.get_response(request)