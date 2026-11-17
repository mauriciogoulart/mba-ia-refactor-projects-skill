"""Criação do schema e seed de dados de demonstração."""
import logging

from werkzeug.security import generate_password_hash

from database.connection import conectar

logger = logging.getLogger(__name__)

# Restrições valem para bancos novos; bancos existentes não são migrados (CREATE TABLE IF NOT EXISTS).
DDL = (
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        preco REAL NOT NULL,
        estoque INTEGER NOT NULL,
        categoria TEXT NOT NULL,
        ativo INTEGER DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL,
        tipo TEXT NOT NULL DEFAULT 'cliente',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
        status TEXT NOT NULL DEFAULT 'pendente',
        total REAL NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL REFERENCES pedidos(id),
        produto_id INTEGER NOT NULL,
        quantidade INTEGER NOT NULL,
        preco_unitario REAL NOT NULL
    )
    """,
)

PRODUTOS_DEMO = (
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
)


def _usuarios_demo(settings):
    usuarios = []
    if settings.SEED_ADMIN_PASSWORD:
        usuarios.append(("Admin", "admin@loja.com", settings.SEED_ADMIN_PASSWORD, "admin"))
    else:
        logger.warning("Seed do administrador ignorado: SEED_ADMIN_PASSWORD não definida")
    if settings.SEED_CLIENTE_PASSWORD:
        usuarios.append(("João Silva", "joao@email.com", settings.SEED_CLIENTE_PASSWORD, "cliente"))
        usuarios.append(("Maria Santos", "maria@email.com", settings.SEED_CLIENTE_PASSWORD, "cliente"))
    else:
        logger.warning("Seed de clientes ignorado: SEED_CLIENTE_PASSWORD não definida")
    return usuarios


def inicializar_banco(settings):
    conexao = conectar(settings.DB_PATH)
    try:
        with conexao:
            for comando in DDL:
                conexao.execute(comando)
            if conexao.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
                conexao.executemany(
                    "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                    PRODUTOS_DEMO,
                )
            if conexao.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
                conexao.executemany(
                    "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                    [(n, e, generate_password_hash(s), t) for n, e, s, t in _usuarios_demo(settings)],
                )
    finally:
        conexao.close()
