const { PAYMENT_STATUS } = require('../config/constants');
const { maskCard } = require('../utils/logger');

// Cartões de teste iniciados por este prefixo são aprovados pelo gateway simulado.
const SIMULATED_APPROVED_PREFIX = '4';

// GATEWAY SIMULADO: não realiza cobrança. Substituir por integração real com o provedor
// de pagamentos antes de uso em produção (finding F-003, residual).
function createSimulatedPaymentGateway({ logger }) {
    return {
        async charge({ cardNumber, amountCents }) {
            const status = cardNumber.startsWith(SIMULATED_APPROVED_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
            logger.info('pagamento simulado processado', { card: maskCard(cardNumber), amountCents, status });
            return status;
        },
    };
}

module.exports = { createSimulatedPaymentGateway };
