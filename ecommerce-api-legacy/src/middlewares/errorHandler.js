const { STATUS_CODES } = require('node:http');
const { AppError } = require('../utils/appError');

// Encaminha rejeições de handlers async ao tratador central.
const asyncHandler = (fn) => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);

function createErrorHandler(logger) {
    // eslint-disable-next-line no-unused-vars
    return (err, req, res, next) => {
        if (err instanceof AppError) return res.status(err.status).send(err.message);

        // Erros 4xx do parser de corpo (JSON inválido, corpo grande): status preservado, sem detalhe interno.
        if (err.status >= 400 && err.status < 500) return res.status(err.status).send(STATUS_CODES[err.status]);

        logger.error('erro não tratado', { error: err.message, stack: err.stack, method: req.method, path: req.path });
        return res.status(500).send('Erro interno');
    };
}

module.exports = { asyncHandler, createErrorHandler };
