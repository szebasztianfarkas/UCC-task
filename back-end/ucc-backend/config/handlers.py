from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import JsonResponse


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, ValidationError):
        return Response(
            {'detail': exc.message if hasattr(exc, 'message') else str(exc)},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return None


def bad_request(request, exception=None):
    return JsonResponse({'detail': 'Bad request.'}, status=400)


def permission_denied(request, exception=None):
    return JsonResponse({'detail': 'Permission denied.'}, status=403)


def not_found(request, exception=None):
    return JsonResponse({'detail': 'Not found.'}, status=404)


def server_error(request):
    return JsonResponse({'detail': 'A server error occurred.'}, status=500)