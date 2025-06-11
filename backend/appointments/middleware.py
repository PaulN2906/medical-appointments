"""
Transaction Monitoring Middleware for Thesis Demonstration
This middleware helps demonstrate transaction control and resource access patterns.

Create this file at: backend/appointments/middleware.py
"""

import time
import logging
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.db import transaction

logger = logging.getLogger('appointments')

class TransactionMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware to monitor and log transaction behavior for thesis demonstration
    """
    
    def process_request(self, request):
        # Add unique request ID for tracking
        request.transaction_id = str(uuid.uuid4())[:8]
        request.start_time = time.time()
        
        # Log requests to appointment endpoints
        if '/appointments/' in request.path:
            logger.info(f"[{request.transaction_id}] {request.method} {request.path} - Transaction started")
        
        return None
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time') and '/appointments/' in request.path:
            duration = time.time() - request.start_time
            
            # Log transaction completion
            logger.info(
                f"[{getattr(request, 'transaction_id', 'unknown')}] "
                f"Transaction completed - Status: {response.status_code}, "
                f"Duration: {duration:.3f}s"
            )
            
            # Add custom headers for debugging (only in DEBUG mode)
            from django.conf import settings
            if settings.DEBUG:
                response['X-Transaction-ID'] = getattr(request, 'transaction_id', 'unknown')
                response['X-Transaction-Duration'] = f"{duration:.3f}s"
        
        return response
    
    def process_exception(self, request, exception):
        if hasattr(request, 'start_time') and '/appointments/' in request.path:
            duration = time.time() - request.start_time
            
            # Log transaction failure
            logger.error(
                f"[{getattr(request, 'transaction_id', 'unknown')}] "
                f"Transaction failed - Exception: {str(exception)}, "
                f"Duration: {duration:.3f}s"
            )
        
        return None
