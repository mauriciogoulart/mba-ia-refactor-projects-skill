from flask import jsonify, request

from middleware.auth import current_user
from services import category_service
from validators.category_validator import parse_category_update, parse_new_category
from validators.common import parse_pagination
from views.serializers import category_to_dict


def list_categories():
    limit, offset = parse_pagination(request.args)
    categories = category_service.list_categories(limit, offset, current_user().task_scope())
    return jsonify([{**category_to_dict(category), 'task_count': total} for category, total in categories]), 200


def create_category():
    category = category_service.create_category(parse_new_category(request.get_json()))
    return jsonify(category_to_dict(category)), 201


def update_category(category_id):
    category_service.ensure_exists(category_id)
    category = category_service.update_category(category_id, parse_category_update(request.get_json()))
    return jsonify(category_to_dict(category)), 200


def delete_category(category_id):
    category_service.delete_category(category_id)
    return jsonify({'message': 'Categoria deletada'}), 200
