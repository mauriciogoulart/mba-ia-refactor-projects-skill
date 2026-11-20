// F-006, F-010 e F-013: aplicações montadas por injeção, sem estado global compartilhado.
const { describe, it, after } = require('node:test');
const assert = require('node:assert/strict');
const { createApplication } = require('../src/app');
const { loadSettings } = require('../src/config/settings');

const logger = { info() {}, warn() {}, error() {} };
const CHAVE = 'chave-do-teste';
const settings = loadSettings({
    APP_ENV: 'test',
    PAYMENT_PROVIDER: 'mock',
    PAYMENT_MOCK_APPROVED_PREFIXES: '4',
    ADMIN_API_KEY: CHAVE,
    SEED_USER_PASSWORD: 'senha-de-seed-do-teste',
});

async function subir() {
    const { app, db } = await createApplication(settings, logger);
    const server = await new Promise((resolve) => {
        const s = app.listen(0, '127.0.0.1', () => resolve(s));
    });
    return { db, server, base: `http://127.0.0.1:${server.address().port}` };
}

const receitaDocker = async (base) => {
    const r = await fetch(`${base}/api/admin/financial-report`, { headers: { Authorization: `Bearer ${CHAVE}` } });
    return (await r.json()).find((c) => c.course === 'Docker').revenue;
};

describe('composition root', () => {
    const instancias = [];

    after(async () => {
        for (const { server, db } of instancias) {
            server.closeAllConnections();
            await new Promise((resolve) => server.close(resolve));
            await db.close();
        }
    });

    it('duas aplicações no mesmo processo não compartilham estado', async () => {
        const [a, b] = [await subir(), await subir()];
        instancias.push(a, b);

        const r = await fetch(`${a.base}/api/checkout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usr: 'Ana', eml: 'ana@teste.com', pwd: 'senha-ana', c_id: 2, card: '4111222233334444' }),
        });
        assert.equal(r.status, 200);
        assert.equal(await receitaDocker(a.base), 497);
        assert.equal(await receitaDocker(b.base), 0);
    });
});
