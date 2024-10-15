from django.shortcuts import render
from django_ratelimit.exceptions import Ratelimited


class RatelimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, Ratelimited):
            return render(request, "ratelimit_error.html", status=429)


class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if response.status_code == 404:
            return render(request, "404.html", status=404)

        return response
