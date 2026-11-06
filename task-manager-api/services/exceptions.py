class AppError(Exception):
    """Erro de domínio traduzido pelo handler central em resposta JSON {'error': ...}."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
