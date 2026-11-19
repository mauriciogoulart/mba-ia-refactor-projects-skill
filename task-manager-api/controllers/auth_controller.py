from flask import current_app, jsonify, request

from services import auth_service
from validators.user_validator import parse_credentials
from views.serializers import user_to_public


def login():
    email, password = parse_credentials(request.get_json())
    throttle = current_app.extensions['login_throttle']
    user = auth_service.authenticate(email, password, throttle, request.remote_addr)
    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user_to_public(user),
        'token': current_app.extensions['token_service'].issue(user),
    }), 200
