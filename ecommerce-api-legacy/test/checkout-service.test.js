// F-005, F-008, F-009, F-010 e F-011: regra de checkout testável sem HTTP, com dependências injetadas.
const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const { openDatabase } = require('../src/database/connection');
const { createSchema, seedDatabase } = require('../src/database/schema');
const { createUserModel } = require('../src/models/userModel');
const { createCourseModel } = require('../src/models/courseModel');
const { createEnrollmentModel } = require('../src/models/enrollmentModel');
const { createPaymentModel } = require('../src/models/paymentModel');
const { createAuditLogModel } = require('../src/models/auditLogModel');
const { createPasswordService } = require('../src/services/passwordService');
const { createCheckoutService } = require('../src/services/checkoutService');

const logger = { info() {}, warn() {}, error() {} };
const passwordService = createPasswordService();
const SENHA_SEED = 'senha-de-seed-do-teste';
const aprovado = { charge: async () => ({ status: 'PAID' }) };
const recusado = { charge: async () => ({ status: 'DENIED' }) };
const compra = { name: 'Nova', email: 'nova@teste.com', password: 'senha-nova', courseId: 2, cardNumber: '4111222233334444' };

describe('checkoutService', () => {
    let db;

    const criarServico = (sobrescritas = {}) => createCheckoutService({
        db,
        userModel: createUserModel(db),
        courseModel: createCourseModel(db),
        enrollmentModel: createEnrollmentModel(db),
        paymentModel: createPaymentModel(db),
        auditLogModel: createAuditLogModel(db),
        paymentGateway: aprovado,
        passwordService,
        logger,
        ...sobrescritas,
    });
    const contar = async (tabela) => (await db.get(`SELECT COUNT(*) AS total FROM ${tabela}`)).total;

    beforeEach(async () => {
        db = await openDatabase(':memory:');
        await createSchema(db);
        await seedDatabase(db, { seedUserPassword: SENHA_SEED, passwordService, logger });
    });

    afterEach(() => db.close());

    it('F-011: conclui a compra e grava usuário, matrícula, pagamento e auditoria', async () => {
        const { enrollmentId } = await criarServico().checkout(compra);
        assert.equal(typeof enrollmentId, 'number');
        assert.equal(await contar('users'), 2);
        assert.equal(await contar('enrollments'), 2);
        assert.equal(await contar('payments'), 2);
        assert.equal(await contar('audit_logs'), 1);
    });

    it('F-009: pagamento recusado não grava nada, nem o usuário novo', async () => {
        await assert.rejects(criarServico({ paymentGateway: recusado }).checkout(compra), { status: 400, message: 'Pagamento recusado' });
        assert.equal(await contar('users'), 1);
        assert.equal(await contar('enrollments'), 1);
    });

    it('F-009: falha no meio do fluxo desfaz todas as escritas', async () => {
        const paymentModel = { create: async () => { throw new Error('falha simulada'); } };
        await assert.rejects(criarServico({ paymentModel }).checkout(compra), /falha simulada/);
        assert.equal(await contar('users'), 1);
        assert.equal(await contar('enrollments'), 1);
        assert.equal(await contar('payments'), 1);
    });

    it('F-008: e-mail cadastrado com senha errada é negado antes de cobrar', async () => {
        let cobrancas = 0;
        const paymentGateway = { charge: async () => { cobrancas += 1; return { status: 'PAID' }; } };
        const dados = { ...compra, email: 'leonan@fullcycle.com.br', password: 'senha-errada' };
        await assert.rejects(criarServico({ paymentGateway }).checkout(dados), { status: 401 });
        assert.equal(cobrancas, 0);
        assert.equal(await contar('enrollments'), 1);
    });

    it('F-008: e-mail cadastrado com a senha correta conclui a compra', async () => {
        const dados = { ...compra, email: 'leonan@fullcycle.com.br', password: SENHA_SEED };
        await criarServico().checkout(dados);
        assert.equal(await contar('users'), 1);
        assert.equal(await contar('enrollments'), 2);
    });

    it('F-005: compra sem senha não cria conta com senha padrão', async () => {
        await criarServico().checkout({ ...compra, password: '' });
        const { pass } = await db.get('SELECT pass FROM users WHERE email = ?', [compra.email]);
        assert.match(pass, /^scrypt\$/);
        assert.equal(await passwordService.verify('123456', pass), false);
    });
});
