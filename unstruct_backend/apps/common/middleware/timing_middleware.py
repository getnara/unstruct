import time
from django.db import connection

class ServerTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timing the entire request
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        # Calculate total request duration
        total_duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Get database query timing
        db_time = sum(float(query.get('time', 0)) for query in connection.queries) * 1000
        
        # Add Server-Timing header
        timing_headers = [
            f"total;dur={total_duration:.2f};desc='Total Response Time'",
            f"db;dur={db_time:.2f};desc='Database Time'",
            f"app;dur={(total_duration - db_time):.2f};desc='Application Time'"
        ]
        
        response['Server-Timing'] = ', '.join(timing_headers)
        return response

class ViewTimingContextManager:
    def __init__(self, name):
        self.name = name
        self.start_time = None
        self.duration = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = (time.time() - self.start_time) * 1000  # Convert to milliseconds 