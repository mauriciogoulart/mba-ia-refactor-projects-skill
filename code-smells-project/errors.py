"""Erros de domínio traduzidos para resposta HTTP pelo handler central."""


class AppError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
