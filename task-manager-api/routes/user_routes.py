from flask import Blueprint

from controllers import auth_controller, user_controller
from middleware.auth import admin_required, login_required, optional_auth, self_or_staff_required, staff_required

user_bp = Blueprint('users', __name__)

user_bp.add_url_rule('/users', 'get_users', staff_required(user_controller.list_users), methods=['GET'])
user_bp.add_url_rule('/users', 'create_user', optional_auth(user_controller.create_user), methods=['POST'])
user_bp.add_url_rule('/users/<int:user_id>', 'get_user', self_or_staff_required(user_controller.get_user), methods=['GET'])
user_bp.add_url_rule('/users/<int:user_id>', 'update_user', login_required(user_controller.update_user), methods=['PUT'])
user_bp.add_url_rule('/users/<int:user_id>', 'delete_user', admin_required(user_controller.delete_user), methods=['DELETE'])
user_bp.add_url_rule('/users/<int:user_id>/tasks', 'get_user_tasks', self_or_staff_required(user_controller.get_user_tasks), methods=['GET'])
user_bp.add_url_rule('/login', 'login', auth_controller.login, methods=['POST'])
