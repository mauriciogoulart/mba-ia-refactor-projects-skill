from flask import Blueprint

from constants import TIPO_ADMIN
from controllers import relatorio_controller as controller
from middlewares.auth import exigir_perfil

blueprint = Blueprint("relatorios", __name__)

blueprint.add_url_rule(
    "/relatorios/vendas", "vendas", exigir_perfil(TIPO_ADMIN)(controller.vendas), methods=["GET"]
)
