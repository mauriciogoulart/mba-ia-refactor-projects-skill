"""Registro central das rotas (mapeamento método + caminho → controller)."""
from routes.pedido_routes import blueprint as pedido_bp
from routes.produto_routes import blueprint as produto_bp
from routes.relatorio_routes import blueprint as relatorio_bp
from routes.sistema_routes import blueprint as sistema_bp
from routes.usuario_routes import blueprint as usuario_bp


def registrar_rotas(app):
    for blueprint in (produto_bp, usuario_bp, pedido_bp, relatorio_bp, sistema_bp):
        app.register_blueprint(blueprint)
