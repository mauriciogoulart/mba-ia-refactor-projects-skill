// Cabeçalhos de segurança básicos para uma API JSON (aditivos; não alteram o corpo das respostas).
function securityHeaders(req, res, next) {
    res.set({
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'Referrer-Policy': 'no-referrer',
        'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'",
    });
    next();
}

module.exports = { securityHeaders };
