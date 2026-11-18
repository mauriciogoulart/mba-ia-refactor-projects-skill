const { MESSAGES } = require('../config/constants');
const { AppError } = require('../errors/AppError');

// Tratamento central: mantém respostas de erro em texto e nunca expõe detalhes internos ao cliente.
function createErrorHandler({ logger }) {
    // O quarto parâmetro é obrigatório para o Express reconhecer o middleware de erro.
    return (err, req, res, next) => {
        if (res.headersSent) return next(err);
        if (err instanceof AppError) return res.status(err.status).send(err.message);
        if (err.status >= 400 && err.status < 500) return res.status(err.status).send(MESSAGES.BAD_REQUEST);

        logger.error('erro não tratado', { error: err.message, stack: err.stack });
        return res.status(500).send(MESSAGES.INTERNAL_ERROR);
    };
}

module.exports = { createErrorHandler };
