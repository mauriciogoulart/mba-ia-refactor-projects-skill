// Erro de domínio com status HTTP; a mensagem é segura para o cliente.
class AppError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}

module.exports = { AppError };
