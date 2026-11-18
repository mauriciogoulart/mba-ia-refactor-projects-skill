// Configuração única da aplicação, lida do ambiente. Nenhum segredo literal no código.
function loadSettings(env = process.env) {
    return {
        port: Number(env.PORT || 3000),
        appEnv: String(env.APP_ENV || '').trim(),
        databaseFile: env.DATABASE_FILE || ':memory:',
        logLevel: env.LOG_LEVEL || 'info',
        // Credencial das rotas administrativas; ausente ⇒ rotas administrativas negam tudo.
        adminApiKey: env.ADMIN_API_KEY || '',
        // Senha do usuário de seed; ausente ⇒ senha aleatória não divulgada (sem credencial padrão).
        seedUserPassword: env.SEED_USER_PASSWORD || '',
        // Pagamento: sem provedor configurado ⇒ recusa (P-20).
        paymentProvider: String(env.PAYMENT_PROVIDER || '').trim(),
        paymentMockApprovedPrefixes: env.PAYMENT_MOCK_APPROVED_PREFIXES || '',
        paymentApiKey: env.PAYMENT_GATEWAY_KEY || '',
        checkoutRateLimit: {
            max: Number(env.CHECKOUT_RATE_LIMIT_MAX || 30),
            windowMs: Number(env.CHECKOUT_RATE_LIMIT_WINDOW_MS || 60000),
        },
    };
}

module.exports = { loadSettings };
