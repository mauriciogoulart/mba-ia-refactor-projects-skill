const { MESSAGES } = require('../config/constants');
const { AppError } = require('../errors/AppError');

const PRUNE_THRESHOLD = 1000;

// Limite por IP em janela fixa; o estado pertence à instância criada no composition root.
function createRateLimiter({ max, windowMs, now = Date.now }) {
    const hits = new Map();

    function prune(currentTime) {
        for (const [key, entry] of hits) {
            if (entry.resetAt <= currentTime) hits.delete(key);
        }
    }

    return (req, res, next) => {
        const currentTime = now();
        if (hits.size >= PRUNE_THRESHOLD) prune(currentTime);

        const current = hits.get(req.ip);
        const entry = current && current.resetAt > currentTime
            ? current
            : { count: 0, resetAt: currentTime + windowMs };
        entry.count += 1;
        hits.set(req.ip, entry);

        if (entry.count > max) {
            res.set('Retry-After', String(Math.ceil((entry.resetAt - currentTime) / 1000)));
            return next(new AppError(MESSAGES.TOO_MANY_REQUESTS, 429));
        }
        return next();
    };
}

module.exports = { createRateLimiter };
