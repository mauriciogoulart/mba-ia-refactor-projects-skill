"""Conexão SQLite por requisição (sem conexão global compartilhada)."""
import sqlite3

from flask import current_app, g


def conectar(caminho):
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    return conexao


def obter_conexao():
    if "db" not in g:
        g.db = conectar(current_app.config["DB_PATH"])
    return g.db


def fechar_conexao(_erro=None):
    conexao = g.pop("db", None)
    if conexao is not None:
        conexao.close()


def init_app(app):
    app.teardown_appcontext(fechar_conexao)
