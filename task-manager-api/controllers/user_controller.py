from flask import jsonify, request

from middleware.auth import current_user
from services import user_service
from validators.common import parse_pagination
from validators.user_validator import parse_new_user, parse_user_update
from views.serializers import task_to_dict, user_task_item, user_to_public


def list_users():
    limit, offset = parse_pagination(request.args)
    users = user_service.list_users(limit, offset)
    return jsonify([{**user_to_public(user), 'task_count': total} for user, total in users]), 200


def get_user(user_id):
    user = user_service.get_user(user_id)
    tasks = user_service.get_user_tasks(user_id)
    return jsonify({**user_to_public(user), 'tasks': [task_to_dict(task) for task in tasks]}), 200


def create_user():
    user = user_service.create_user(parse_new_user(request.get_json()), current_user())
    return jsonify(user_to_public(user)), 201


def update_user(user_id):
    actor = current_user()
    user_service.ensure_can_edit(user_id, actor)
    user_service.get_user(user_id)
    user = user_service.update_user(user_id, parse_user_update(request.get_json()), actor)
    return jsonify(user_to_public(user)), 200


def delete_user(user_id):
    user_service.delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


def get_user_tasks(user_id):
    return jsonify([user_task_item(task) for task in user_service.get_user_tasks(user_id)]), 200
