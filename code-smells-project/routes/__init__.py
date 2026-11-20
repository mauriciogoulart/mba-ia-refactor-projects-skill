"""Mapeamento método + caminho → controller, com a proteção de cada rota."""
from flask import Blueprint

from controllers import pedido_controller, produto_controller, sistema_controller, usuario_controller
from middlewares.auth import exigir_autenticacao
from services.regras import TIPO_ADMIN

admin = exigir_autenticacao(TIPO_ADMIN)
autenticado = exigir_autenticacao()


def _blueprint_produtos():
    bp = Blueprint("produtos", __name__)
    bp.add_url_rule("/produtos", view_func=produto_controller.listar_produtos, methods=["GET"])
    bp.add_url_rule("/produtos/busca", view_func=produto_controller.buscar_produtos, methods=["GET"])
    bp.add_url_rule("/produtos/<int:produto_id>", view_func=produto_controller.buscar_produto, methods=["GET"])
    bp.add_url_rule("/produtos", view_func=admin(produto_controller.criar_produto), methods=["POST"])
    bp.add_url_rule("/produtos/<int:produto_id>", view_func=admin(produto_controller.atualizar_produto),
                    methods=["PUT"])
    bp.add_url_rule("/produtos/<int:produto_id>", view_func=admin(produto_controller.deletar_produto),
                    methods=["DELETE"])
    return bp


def _blueprint_usuarios():
    bp = Blueprint("usuarios", __name__)
    bp.add_url_rule("/usuarios", view_func=admin(usuario_controller.listar_usuarios), methods=["GET"])
    bp.add_url_rule("/usuarios/<int:usuario_id>", view_func=autenticado(usuario_controller.buscar_usuario),
                    methods=["GET"])
    bp.add_url_rule("/usuarios", view_func=usuario_controller.criar_usuario, methods=["POST"])
    bp.add_url_rule("/login", view_func=usuario_controller.login, methods=["POST"])
    return bp


def _blueprint_pedidos():
    bp = Blueprint("pedidos", __name__)
    bp.add_url_rule("/pedidos", view_func=autenticado(pedido_controller.criar_pedido), methods=["POST"])
    bp.add_url_rule("/pedidos", view_func=admin(pedido_controller.listar_todos_pedidos), methods=["GET"])
    bp.add_url_rule("/pedidos/usuario/<int:usuario_id>",
                    view_func=autenticado(pedido_controller.listar_pedidos_usuario), methods=["GET"])
    bp.add_url_rule("/pedidos/<int:pedido_id>/status",
                    view_func=admin(pedido_controller.atualizar_status_pedido), methods=["PUT"])
    return bp


def _blueprint_sistema():
    bp = Blueprint("sistema", __name__)
    bp.add_url_rule("/", view_func=sistema_controller.index, methods=["GET"])
    bp.add_url_rule("/health", view_func=sistema_controller.health_check, methods=["GET"])
    bp.add_url_rule("/relatorios/vendas", view_func=admin(sistema_controller.relatorio_vendas), methods=["GET"])
    bp.add_url_rule("/admin/reset-db", view_func=admin(sistema_controller.reset_database), methods=["POST"])
    return bp


def registrar_rotas(app):
    for fabrica in (_blueprint_produtos, _blueprint_usuarios, _blueprint_pedidos, _blueprint_sistema):
        app.register_blueprint(fabrica())
