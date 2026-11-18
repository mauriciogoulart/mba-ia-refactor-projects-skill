// F-002 (SEC-14): a aprovação vem de provedor configurado, com recusa por padrão.
const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { createPaymentGateway } = require('../src/services/payment/gatewayFactory');

const logger = { info() {}, warn() {}, error() {} };
const cobranca = { cardNumber: '4111111111111111', amountCents: 100 };

describe('gateway de pagamento', () => {
    it('sem provedor configurado, qualquer cartão é recusado', async () => {
        const gateway = createPaymentGateway({ settings: { paymentProvider: '' }, logger });
        assert.equal((await gateway.charge(cobranca)).status, 'DENIED');
    });

    it('provedor desconhecido é recusado', async () => {
        const gateway = createPaymentGateway({ settings: { paymentProvider: 'constructor' }, logger });
        assert.equal((await gateway.charge(cobranca)).status, 'DENIED');
    });

    it('mock é bloqueado fora da lista branca de ambientes', () => {
        assert.throws(() => createPaymentGateway({ settings: { paymentProvider: 'mock', appEnv: 'production' }, logger }));
        assert.throws(() => createPaymentGateway({ settings: { paymentProvider: 'mock' }, logger }));
    });

    it('mock aprova só os prefixos configurados; lista vazia não aprova nada', async () => {
        const settings = { paymentProvider: 'mock', appEnv: 'test', paymentMockApprovedPrefixes: '4' };
        const gateway = createPaymentGateway({ settings, logger });
        assert.equal((await gateway.charge(cobranca)).status, 'PAID');
        assert.equal((await gateway.charge({ ...cobranca, cardNumber: '5111111111111111' })).status, 'DENIED');

        const vazio = createPaymentGateway({ settings: { ...settings, paymentMockApprovedPrefixes: '' }, logger });
        assert.equal((await vazio.charge(cobranca)).status, 'DENIED');
    });
});
