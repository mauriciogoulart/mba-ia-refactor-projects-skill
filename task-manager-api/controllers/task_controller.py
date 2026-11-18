from flask import jsonify, request

from middleware.auth import current_user
from services import task_service
from validators.common import parse_pagination
from validators.task_validator import parse_new_task, parse_search_filters, parse_task_update
from views.serializers import task_detail, task_list_item, task_to_dict


def list_tasks():
    limit, offset = parse_pagination(request.args)
    return jsonify([task_list_item(task) for task in task_service.list_tasks(limit, offset)]), 200


def get_task(task_id):
    return jsonify(task_detail(task_service.get_task(task_id))), 200


def create_task():
    task = task_service.create_task(parse_new_task(request.get_json()))
    return jsonify(task_to_dict(task)), 201


def update_task(task_id):
    task = task_service.get_task_for_change(task_id, current_user())
    task = task_service.update_task(task, parse_task_update(request.get_json()))
    return jsonify(task_to_dict(task)), 200


def delete_task(task_id):
    task_service.delete_task(task_service.get_task_for_change(task_id, current_user()))
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    filters = parse_search_filters(request.args)
    limit, offset = parse_pagination(request.args)
    return jsonify([task_to_dict(task) for task in task_service.search_tasks(filters, limit, offset)]), 200


def task_stats():
    return jsonify(task_service.get_stats()), 200
