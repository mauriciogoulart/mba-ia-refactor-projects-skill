const { PAYMENT_STATUS } = require('../../config/constants');
const { cardLast4 } = require('../../utils/logger');

// Gateway de pagamento por configuração com recusa por padrão (P-20).
const MOCK_ALLOWED_ENVS = new Set(['test', 'development']); // lista branca; ambiente ausente bloqueia
const PROVIDERS = new Map(); // integrações reais registradas aqui (nenhuma existe neste projeto)

const parsePrefixes = (raw) => String(raw || '').split(',').map((p) => p.trim()).filter(Boolean);

function createPaymentGateway({ settings, logger }) {
    const provider = String(settings.paymentProvider || '').trim();
    if (provider === 'mock') {
        if (!MOCK_ALLOWED_ENVS.has(settings.appEnv)) {
            throw new Error('PAYMENT_PROVIDER=mock só é permitido com APP_ENV=test ou development');
        }
        return createMockGateway({ approvedPrefixes: parsePrefixes(settings.paymentMockApprovedPrefixes), logger });
    }
    if (PROVIDERS.has(provider)) return PROVIDERS.get(provider)({ apiKey: settings.paymentApiKey, logger });
    return createUnavailableGateway({ logger });
}

function createUnavailableGateway({ logger }) {
    return {
        async charge() {
            logger.warn('pagamento recusado: nenhum provedor de pagamento configurado');
            return { status: PAYMENT_STATUS.DENIED, reason: 'provider_not_configured' };
        },
    };
}

function createMockGateway({ approvedPrefixes, logger }) {
    return {
        async charge({ cardNumber, amountCents }) {
            const approved = approvedPrefixes.some((prefix) => cardNumber.startsWith(prefix));
            logger.info('pagamento MOCK (ambiente de teste)', { last4: cardLast4(cardNumber), amountCents, approved });
            return { status: approved ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED, reason: approved ? null : 'mock_denied' };
        },
    };
}

module.exports = { createPaymentGateway };
