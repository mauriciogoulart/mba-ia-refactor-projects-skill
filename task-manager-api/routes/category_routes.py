from flask import Blueprint

from controllers import category_controller
from middleware.auth import admin_required, login_required

category_bp = Blueprint('categories', __name__)

category_bp.add_url_rule('/categories', 'get_categories', login_required(category_controller.list_categories), methods=['GET'])
category_bp.add_url_rule('/categories', 'create_category', login_required(category_controller.create_category), methods=['POST'])
category_bp.add_url_rule('/categories/<int:category_id>', 'update_category', login_required(category_controller.update_category), methods=['PUT'])
category_bp.add_url_rule('/categories/<int:category_id>', 'delete_category', admin_required(category_controller.delete_category), methods=['DELETE'])
