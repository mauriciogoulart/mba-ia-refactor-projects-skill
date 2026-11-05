from flask import Blueprint

from constants import TIPO_ADMIN
from controllers import sistema_controller as controller
from middlewares.auth import exigir_perfil

blueprint = Blueprint("sistema", __name__)

blueprint.add_url_rule("/", "raiz", controller.raiz, methods=["GET"])
blueprint.add_url_rule("/health", "health", controller.health, methods=["GET"])
blueprint.add_url_rule(
    "/admin/reset-db", "resetar_banco", exigir_perfil(TIPO_ADMIN)(controller.resetar_banco), methods=["POST"]
)
