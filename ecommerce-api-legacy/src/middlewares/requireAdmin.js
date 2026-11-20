const crypto = require('node:crypto');
const { MESSAGES } = require('../config/constants');
const { AppError } = require('../errors/AppError');

const digest = (value) => crypto.createHash('sha256').update(value).digest();

// Exige `Authorization: Bearer <ADMIN_API_KEY>`. Sem chave configurada, nega todas as requisições.
function createRequireAdmin({ adminApiKey }) {
    return (req, res, next) => {
        const match = /^Bearer\s+(.+)$/i.exec(req.get('authorization') || '');
        const authorized = Boolean(adminApiKey) && match !== null
            && crypto.timingSafeEqual(digest(match[1]), digest(adminApiKey));
        if (authorized) return next();

        res.set('WWW-Authenticate', 'Bearer');
        return next(new AppError(MESSAGES.UNAUTHORIZED, 401));
    };
}

module.exports = { createRequireAdmin };
