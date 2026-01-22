from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import redirect
from rest_framework.views import exception_handler
from rest_framework.exceptions import PermissionDenied, NotFound, NotAuthenticated

from core.views import raise403, raise404


def custom_exception_handler(exception, context):
    """
    Custom exception handler.
    """

    # Get the request
    request = context["request"]

    # Check exception type
    if isinstance(exception, PermissionDenied):
        # Return the 403 error page
        return raise403(request, exception)
    elif isinstance(exception, NotAuthenticated):
        # Return the homepage with a message
        messages.add_message(request, messages.WARNING, "Veuillez vous connecter.")
        return redirect("core:home-list")
    elif isinstance(exception, Http404) or isinstance(exception, NotFound):
        # Return the 404 error page
        return raise404(request, exception)

    # Let DRF handle the exception it is not covered
    response = exception_handler(exception, context)

    # Return DRF response
    return response