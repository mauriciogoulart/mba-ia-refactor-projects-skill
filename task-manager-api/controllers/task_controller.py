from flask import jsonify, request

from controllers import validators
from services import task_service
from utils.helpers import utc_now
from views.serializers import task_list_item, task_to_dict, task_with_overdue


def list_tasks():
    now = utc_now()
    return jsonify([task_list_item(task, now) for task in task_service.list_tasks()]), 200


def get_task(task_id):
    task = task_service.get_task(task_id)
    return jsonify(task_with_overdue(task, utc_now())), 200


def create_task():
    fields = validators.parse_task_create(request.get_json())
    task = task_service.create_task(fields)
    return jsonify(task_to_dict(task)), 201


def update_task(task_id):
    task_service.get_task(task_id)
    fields = validators.parse_task_update(request.get_json())
    task = task_service.update_task(task_id, fields)
    return jsonify(task_to_dict(task)), 200


def delete_task(task_id):
    task_service.delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    criteria = validators.parse_search_args(request.args)
    tasks = task_service.search_tasks(**criteria)
    return jsonify([task_to_dict(task) for task in tasks]), 200


def task_stats():
    return jsonify(task_service.task_stats()), 200
