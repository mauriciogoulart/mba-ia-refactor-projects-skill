from flask import Blueprint

from controllers import usuario_controller as controller
from middlewares.security import limitar_tentativas

blueprint = Blueprint("usuarios", __name__)

blueprint.add_url_rule("/usuarios", "listar", controller.listar, methods=["GET"])
blueprint.add_url_rule("/usuarios/<int:usuario_id>", "buscar_por_id", controller.buscar_por_id, methods=["GET"])
blueprint.add_url_rule("/usuarios", "criar", controller.criar, methods=["POST"])
blueprint.add_url_rule("/login", "login", limitar_tentativas(controller.login), methods=["POST"])
