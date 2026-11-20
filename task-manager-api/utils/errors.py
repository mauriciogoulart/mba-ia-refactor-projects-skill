class AppError(Exception):
    """Erro de negócio ou validação traduzido em resposta pelo handler central."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status
