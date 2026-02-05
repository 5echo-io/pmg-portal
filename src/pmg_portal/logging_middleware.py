"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Logging middleware for debugging
Path: src/pmg_portal/logging_middleware.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
import time
import json
import logging
from django.utils.deprecation import MiddlewareMixin
from django.db import connection

logger = logging.getLogger('pmg_portal.debug')


class DebugLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests, responses, database queries, and processing times.
    Stores logs in memory for debug view access.
    """
    # In-memory log storage (last 100 requests)
    _request_logs = []
    _max_logs = 100
    
    def process_request(self, request):
        """Log incoming request details."""
        request._start_time = time.time()
        request._db_queries_before = len(connection.queries)
        request._view_info = {}
        
        log_entry = {
            'timestamp': time.time(),
            'method': request.method,
            'path': request.path,
            'query_string': request.GET.urlencode(),
            'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            'ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referer': request.META.get('HTTP_REFERER', ''),
            'get_keys': list(request.GET.keys()),
            'post_keys': list(request.POST.keys()),
            'content_type': request.META.get('CONTENT_TYPE', ''),
            'content_length': request.META.get('CONTENT_LENGTH', ''),
            'view': None,
            'status': 'processing',
            'db_queries': [],
            'template_rendered': None,
            'processing_time': None,
            'response_size': None,
        }
        
        request._log_entry = log_entry
        logger.info(f"Request: {request.method} {request.path} - User: {log_entry['user']}")
        
        return None

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Capture resolved view information."""
        try:
            resolver_match = getattr(request, 'resolver_match', None)
            view_info = {
                'view_func': getattr(view_func, '__name__', str(view_func)),
                'view_module': getattr(view_func, '__module__', ''),
                'view_args': view_args,
                'view_kwargs': view_kwargs,
                'url_name': getattr(resolver_match, 'url_name', None),
                'app_name': getattr(resolver_match, 'app_name', None),
                'namespace': getattr(resolver_match, 'namespace', None),
                'view_name': getattr(resolver_match, 'view_name', None),
            }
            request._view_info = view_info
            if hasattr(request, '_log_entry'):
                request._log_entry['view'] = view_info
        except Exception:
            # Avoid breaking request handling due to logging errors
            pass
        return None

    def process_template_response(self, request, response):
        """Capture template names and context keys for template responses."""
        if hasattr(request, '_log_entry'):
            try:
                templates = getattr(response, 'templates', []) or []
                template_names = []
                for t in templates:
                    name = getattr(t, 'name', None)
                    if name:
                        template_names.append(name)
                context_keys = []
                context_data = getattr(response, 'context_data', None)
                if isinstance(context_data, dict):
                    context_keys = list(context_data.keys())
                request._log_entry['template_rendered'] = template_names or None
                request._log_entry['context_keys'] = context_keys
            except Exception:
                pass
        return response
    
    def process_response(self, request, response):
        """Log response details."""
        if hasattr(request, '_log_entry'):
            processing_time = time.time() - request._start_time
            db_queries_after = len(connection.queries)
            db_queries_count = db_queries_after - request._db_queries_before
            db_queries = connection.queries[-db_queries_count:] if db_queries_count > 0 else []
            db_time_ms = 0.0
            slow_queries = []
            for query in db_queries:
                try:
                    q_time = float(query.get('time', 0)) * 1000
                    db_time_ms += q_time
                    if q_time >= 200:
                        slow_queries.append({
                            'time_ms': round(q_time, 2),
                            'sql': query.get('sql', '')[:500],
                        })
                except Exception:
                    continue
            
            request._log_entry.update({
                'status': 'completed',
                'status_code': response.status_code,
                'db_queries_count': db_queries_count,
                'db_queries': db_queries,
                'db_time_ms': round(db_time_ms, 2),
                'slow_queries': slow_queries,
                'processing_time': round(processing_time * 1000, 2),  # milliseconds
                'response_size': len(response.content) if hasattr(response, 'content') else 0,
                'response_content_type': getattr(response, 'get', lambda x, d=None: None)('Content-Type', None),
            })
            
            # Add to logs (keep only last N)
            self._request_logs.append(request._log_entry)
            if len(self._request_logs) > self._max_logs:
                self._request_logs.pop(0)
            
            logger.info(
                f"Response: {request.method} {request.path} - "
                f"Status: {response.status_code} - "
                f"Time: {processing_time*1000:.2f}ms - "
                f"DB Queries: {db_queries_count}"
            )
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions."""
        if hasattr(request, '_log_entry'):
            request._log_entry.update({
                'status': 'error',
                'exception': str(exception),
                'exception_type': type(exception).__name__,
            })
            logger.error(f"Exception in {request.path}: {exception}", exc_info=True)
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @classmethod
    def get_logs(cls, limit=50):
        """Get recent logs for debug view."""
        return cls._request_logs[-limit:]
    
    @classmethod
    def clear_logs(cls):
        """Clear all logs."""
        cls._request_logs = []
