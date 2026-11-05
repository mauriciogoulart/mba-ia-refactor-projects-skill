from flask import Blueprint

from controllers import produto_controller as controller

blueprint = Blueprint("produtos", __name__)

blueprint.add_url_rule("/produtos", "listar", controller.listar, methods=["GET"])
blueprint.add_url_rule("/produtos/busca", "buscar", controller.buscar, methods=["GET"])
blueprint.add_url_rule("/produtos/<int:produto_id>", "buscar_por_id", controller.buscar_por_id, methods=["GET"])
blueprint.add_url_rule("/produtos", "criar", controller.criar, methods=["POST"])
blueprint.add_url_rule("/produtos/<int:produto_id>", "atualizar", controller.atualizar, methods=["PUT"])
blueprint.add_url_rule("/produtos/<int:produto_id>", "deletar", controller.deletar, methods=["DELETE"])
