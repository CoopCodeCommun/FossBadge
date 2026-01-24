import sweetify
from django.contrib import messages



class ShowMessagesMiddleware:
    """
    Middleware for showing messages
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        message = messages.get_messages(request)
        for msg in message:
            sweetify.toast(request, msg.message, icon=msg.level_tag)


        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
