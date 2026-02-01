"""
WSGI entry point for Vercel deployment
Uses serverless function format
"""

from app import app

# Vercel will call this function for each request
def handler(request):
    """Vercel serverless function handler"""
    with app.app_context():
        return app(request.environ, request.start_response)
