from django.http import Http404
from django.shortcuts import render
from django.utils.deprecation import MiddlewareMixin

class Handle404Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response.status_code == 404:
            return render(request, 'error/404.html', status=404)
        return response
