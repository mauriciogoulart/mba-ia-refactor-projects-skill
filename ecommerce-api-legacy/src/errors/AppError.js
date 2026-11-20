// Erro de domínio com status HTTP; a mensagem é segura para o cliente.
class AppError extends Error {
    constructor(message, status = 400) {
        super(message);
        this.name = 'AppError';
        this.status = status;
    }
}

module.exports = { AppError };
