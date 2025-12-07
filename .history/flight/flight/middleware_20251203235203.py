# flight/middleware.py
import time
from .metrics import record_request

class PrometheusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        elapsed = time.time() - start

        # Use path_info or name; keep it simple: endpoint = request.path
        endpoint = request.path
        method = request.method
        status = getattr(response, "status_code", 200)
        record_request(method, endpoint, status, elapsed)
        return response
