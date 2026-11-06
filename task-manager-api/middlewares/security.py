"""Proteções HTTP: CORS por lista de origens e cabeçalhos de segurança."""
from flask_cors import CORS

SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'no-referrer',
}


def register_security(app, settings):
    CORS(app, origins=settings.CORS_ORIGINS)

    @app.after_request
    def add_security_headers(response):
        for name, value in SECURITY_HEADERS.items():
            response.headers.setdefault(name, value)
        return response
