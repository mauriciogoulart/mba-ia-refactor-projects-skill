"""Exceção de domínio traduzida para resposta HTTP pelo handler central."""


class AppError(Exception):
    def __init__(self, mensagem, status=400):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.status = status
