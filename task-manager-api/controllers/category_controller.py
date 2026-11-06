from flask import jsonify, request

from controllers import validators
from services import category_service
from views.serializers import category_to_dict


def list_categories():
    categories = category_service.list_categories_with_task_count()
    return jsonify([category_to_dict(category, count) for category, count in categories]), 200


def create_category():
    fields = validators.parse_category_create(request.get_json())
    category = category_service.create_category(fields)
    return jsonify(category_to_dict(category)), 201


def update_category(category_id):
    category_service.get_category(category_id)
    fields = validators.parse_category_update(request.get_json())
    category = category_service.update_category(category_id, fields)
    return jsonify(category_to_dict(category)), 200


def delete_category(category_id):
    category_service.delete_category(category_id)
    return jsonify({'message': 'Categoria deletada'}), 200
