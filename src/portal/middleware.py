"""
Copyright (c) 2026 5echo.io
Project: PMG Portal
Purpose: Custom middleware for language preference
Path: src/portal/middleware.py
Created: 2026-02-05
Last Modified: 2026-02-05
"""
from django.utils import translation
from django.conf import settings


class LanguagePreferenceMiddleware:
    """Middleware to handle user language preference."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # If user is authenticated and has a preferred language in session, use it
        if request.user.is_authenticated:
            preferred_lang = request.session.get('user_preferred_language')
            if preferred_lang and preferred_lang in dict(settings.LANGUAGES):
                translation.activate(preferred_lang)
                request.session[translation.LANGUAGE_SESSION_KEY] = preferred_lang
        
        response = self.get_response(request)
        return response
