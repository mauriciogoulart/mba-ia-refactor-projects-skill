from flask import current_app, g, jsonify, request

from controllers import validators
from middlewares.auth import optional_current_user
from services import auth_service, user_service
from services.exceptions import AppError
from utils.constants import ROLE_USER
from utils.helpers import utc_now
from views.serializers import task_to_dict, user_list_item, user_task_item, user_to_public

FORBIDDEN = 'Sem permissão'
PRIVILEGED_FIELDS = ('role', 'active')


def list_users():
    users = user_service.list_users_with_task_count()
    return jsonify([user_list_item(user, count) for user, count in users]), 200


def get_user(user_id):
    user, tasks = user_service.get_user_with_tasks(user_id)
    data = user_to_public(user)
    data['tasks'] = [task_to_dict(task) for task in tasks]
    return jsonify(data), 200


def create_user():
    fields = validators.parse_user_create(request.get_json())
    if fields['role'] != ROLE_USER:
        caller = optional_current_user()
        if not caller or not caller.is_admin():
            raise AppError(FORBIDDEN, 403)
    user = user_service.create_user(fields)
    return jsonify(user_to_public(user)), 201


def update_user(user_id):
    user = user_service.get_user(user_id)
    caller = g.current_user
    data = request.get_json()
    if not caller.is_admin():
        touches_privileged = isinstance(data, dict) and any(f in data for f in PRIVILEGED_FIELDS)
        if caller.id != user.id or touches_privileged:
            raise AppError(FORBIDDEN, 403)
    fields = validators.parse_user_update(data)
    user = user_service.update_user(user, fields)
    return jsonify(user_to_public(user)), 200


def delete_user(user_id):
    user_service.delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def list_user_tasks(user_id):
    now = utc_now()
    tasks = user_service.list_user_tasks(user_id)
    return jsonify([user_task_item(task, now) for task in tasks]), 200


def login():
    email, password = validators.parse_login(request.get_json())
    user = auth_service.authenticate(email, password)
    token = current_app.extensions['token_signer'].issue(user)
    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user_to_public(user),
        'token': token,
    }), 200
