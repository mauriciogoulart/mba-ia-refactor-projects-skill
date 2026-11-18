from flask import Blueprint

from controllers import report_controller
from middleware.auth import self_or_staff_required, staff_required

report_bp = Blueprint('reports', __name__)

report_bp.add_url_rule('/reports/summary', 'summary_report', staff_required(report_controller.summary_report), methods=['GET'])
report_bp.add_url_rule('/reports/user/<int:user_id>', 'user_report', self_or_staff_required(report_controller.user_report), methods=['GET'])
