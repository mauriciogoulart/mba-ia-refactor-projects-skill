"""Acesso a dados de usuários. A coluna `senha` é de uso interno (nunca serializada)."""

_SELECT = "SELECT id, nome, email, senha, tipo, criado_em FROM usuarios"


def listar(db):
    return [dict(linha) for linha in db.execute(_SELECT).fetchall()]


def obter(db, usuario_id):
    linha = db.execute(_SELECT + " WHERE id = ?", (usuario_id,)).fetchone()
    return dict(linha) if linha else None


def obter_por_email(db, email):
    linha = db.execute(_SELECT + " WHERE email = ?", (email,)).fetchone()
    return dict(linha) if linha else None


def criar(db, nome, email, senha_hash, tipo):
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    return cursor.lastrowid


def atualizar_senha(db, usuario_id, senha_hash):
    db.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (senha_hash, usuario_id))
