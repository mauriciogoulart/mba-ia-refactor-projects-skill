"""Monta os services recebendo a infraestrutura (provedor de conexão) por injeção."""
from services.pedido_service import PedidoService
from services.produto_service import ProdutoService
from services.relatorio_service import RelatorioService
from services.sistema_service import SistemaService
from services.usuario_service import UsuarioService


class Services:
    def __init__(self, obter_db):
        self.produtos = ProdutoService(obter_db)
        self.usuarios = UsuarioService(obter_db)
        self.pedidos = PedidoService(obter_db, self.usuarios)
        self.relatorios = RelatorioService(obter_db)
        self.sistema = SistemaService(obter_db)
