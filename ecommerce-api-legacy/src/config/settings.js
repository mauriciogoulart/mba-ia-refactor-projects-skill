// Configuração central. Valores sensíveis vêm somente do ambiente (ver .env.example).
const env = process.env;

const settings = Object.freeze({
    port: Number(env.PORT || 3000),
    databaseFile: ':memory:',
    // Senha do usuário de seed; se ausente, o boot gera uma senha aleatória (não exibida).
    seedUserPassword: env.SEED_USER_PASSWORD || '',
    logLevel: env.LOG_LEVEL || 'info',
    jsonBodyLimit: '10kb',
    checkoutRateLimit: Object.freeze({
        windowMs: 60 * 1000,
        max: Number(env.CHECKOUT_RATE_MAX || 30),
    }),
});

module.exports = settings;
