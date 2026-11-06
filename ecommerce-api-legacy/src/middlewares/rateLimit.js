// Limite de requisições por IP em janela fixa, em memória (instância única do processo).
function createRateLimiter({ windowMs, max }) {
    const hits = new Map();

    const sweep = setInterval(() => {
        const agora = Date.now();
        for (const [chave, entrada] of hits) if (entrada.resetAt <= agora) hits.delete(chave);
    }, windowMs);
    sweep.unref();

    return (req, res, next) => {
        const agora = Date.now();
        let entrada = hits.get(req.ip);
        if (!entrada || entrada.resetAt <= agora) {
            entrada = { count: 0, resetAt: agora + windowMs };
            hits.set(req.ip, entrada);
        }
        entrada.count += 1;
        if (entrada.count > max) {
            res.set('Retry-After', String(Math.ceil((entrada.resetAt - agora) / 1000)));
            return res.status(429).send('Too Many Requests');
        }
        return next();
    };
}

module.exports = { createRateLimiter };
