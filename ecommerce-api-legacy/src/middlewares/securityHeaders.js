const SECURITY_HEADERS = Object.freeze({
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'Referrer-Policy': 'no-referrer',
    'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'",
    'Cross-Origin-Resource-Policy': 'same-origin',
});

function securityHeaders(req, res, next) {
    res.set(SECURITY_HEADERS);
    next();
}

module.exports = { securityHeaders };
