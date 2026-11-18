from functools import wraps

from flask import current_app, g, request

from services.auth_service import find_active_user
from utils.errors import AppError


def _user_from_request():
    scheme, _, token = request.headers.get('Authorization', '').partition(' ')
    if scheme.lower() != 'bearer' or not token.strip():
        return None
    user_id = current_app.extensions['token_service'].verify(token.strip())
    return find_active_user(user_id) if user_id is not None else None


def current_user():
    return g.get('current_user')


def optional_auth(view):
    """Identifica o chamador quando há token válido, sem exigir autenticação."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        g.current_user = _user_from_request()
        return view(*args, **kwargs)
    return wrapper


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        g.current_user = _user_from_request()
        if g.current_user is None:
            raise AppError('Não autenticado', 401)
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if not g.current_user.is_admin():
            raise AppError('Sem permissão', 403)
        return view(*args, **kwargs)
    return wrapper


def staff_required(view):
    """Restringe a rota aos perfis de gestão (admin e manager)."""
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if not g.current_user.is_staff():
            raise AppError('Sem permissão', 403)
        return view(*args, **kwargs)
    return wrapper


def self_or_staff_required(view):
    """Restringe a rota ao usuário do parâmetro `user_id` e aos perfis de gestão."""
    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        if g.current_user.id != kwargs['user_id'] and not g.current_user.is_staff():
            raise AppError('Sem permissão', 403)
        return view(*args, **kwargs)
    return wrapper
