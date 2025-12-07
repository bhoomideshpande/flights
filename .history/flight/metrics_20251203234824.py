# flight/metrics.py
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client import CollectorRegistry
from django.http import HttpResponse

REQUEST_COUNT = Counter(
    "django_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "http_status"],
)

REQUEST_LATENCY = Histogram(
    "django_http_request_latency_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
)

def record_request(method, endpoint, status, elapsed_seconds):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=str(status)).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed_seconds)

def metrics_view(request):
    # expose all metrics collected by the default registry
    data = generate_latest()
    return HttpResponse(data, content_type=CONTENT_TYPE_LATEST)
