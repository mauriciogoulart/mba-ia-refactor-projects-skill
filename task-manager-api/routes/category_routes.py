from flask import Blueprint

from controllers import category_controller as controller
from middlewares.auth import require_auth

category_bp = Blueprint('categories', __name__)

category_bp.add_url_rule('/categories', view_func=require_auth(controller.list_categories), methods=['GET'])
category_bp.add_url_rule('/categories', view_func=require_auth(controller.create_category), methods=['POST'])
category_bp.add_url_rule('/categories/<int:category_id>', view_func=require_auth(controller.update_category),
                         methods=['PUT'])
category_bp.add_url_rule('/categories/<int:category_id>', view_func=require_auth(controller.delete_category),
                         methods=['DELETE'])
