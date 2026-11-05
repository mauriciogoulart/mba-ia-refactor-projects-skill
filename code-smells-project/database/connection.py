"""Conexão SQLite por requisição (sem estado global compartilhado)."""
import sqlite3

from flask import current_app, g


def criar_conexao(caminho):
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def get_db():
    if "db" not in g:
        g.db = criar_conexao(current_app.config["DB_PATH"])
    return g.db


def close_db(_erro=None):
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()
