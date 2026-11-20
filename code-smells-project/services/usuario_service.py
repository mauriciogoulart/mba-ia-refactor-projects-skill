"""Regras de usuários: cadastro, hash de senha e autenticação."""
import hmac

from werkzeug.security import check_password_hash, generate_password_hash

from services.erros import AppError
from services.regras import TIPO_CLIENTE

PREFIXOS_HASH = ("scrypt:", "pbkdf2:")


def senha_e_hash(valor):
    return isinstance(valor, str) and valor.startswith(PREFIXOS_HASH)


class UsuarioService:
    def __init__(self, usuario_model):
        self._usuarios = usuario_model

    def listar(self, limite=None, offset=0):
        return self._usuarios.listar(limite, offset)

    def obter(self, usuario_id):
        usuario = self._usuarios.obter(usuario_id)
        if usuario is None:
            raise AppError("Usuário não encontrado", 404)
        return usuario

    def existe(self, usuario_id):
        return self._usuarios.obter(usuario_id) is not None

    def identidade(self, usuario_id):
        usuario = self._usuarios.obter(usuario_id)
        return {"id": usuario["id"], "tipo": usuario["tipo"]} if usuario else None

    def criar(self, nome, email, senha):
        if self._usuarios.obter_por_email(email) is not None:
            raise AppError("Email já cadastrado", 400)
        return self._usuarios.criar(nome, email, generate_password_hash(senha), TIPO_CLIENTE)

    def autenticar(self, email, senha):
        """Devolve o usuário se a senha confere; migra senha legada em texto puro para hash."""
        usuario = self._usuarios.obter_por_email(email)
        if usuario is None:
            return None
        armazenada = usuario["senha"] or ""
        if senha_e_hash(armazenada):
            return usuario if check_password_hash(armazenada, senha) else None
        if hmac.compare_digest(armazenada.encode(), senha.encode()):
            self._usuarios.atualizar_senha(usuario["id"], generate_password_hash(senha))
            return usuario
        return None
