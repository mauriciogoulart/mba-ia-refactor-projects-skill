"""Autenticação por token assinado (Authorization: Bearer <token>) e autorização por perfil."""
from functools import wraps

from flask import current_app, g, jsonify, request

from services.auth_service import active_user_from_token

BEARER_PREFIX = 'Bearer '


def optional_current_user():
    header = request.headers.get('Authorization', '')
    token = header[len(BEARER_PREFIX):].strip() if header.startswith(BEARER_PREFIX) else None
    return active_user_from_token(current_app.extensions['token_signer'], token)


def require_auth(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = optional_current_user()
        if not user:
            return jsonify({'error': 'Não autenticado'}), 401
        g.current_user = user
        return view(*args, **kwargs)
    return wrapper


def require_role(*roles):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = optional_current_user()
            if not user:
                return jsonify({'error': 'Não autenticado'}), 401
            if user.role not in roles:
                return jsonify({'error': 'Sem permissão'}), 403
            g.current_user = user
            return view(*args, **kwargs)
        return wrapper
    return decorator
