// F-004 (SEC-02): segredos vêm do ambiente; nenhum literal no código-fonte.
const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const SRC = path.resolve(__dirname, '..', 'src');
const SEGREDOS_LITERAIS = /pk_live_|senha_super_secreta|["']123456["']|VALUES \('Leonan', 'leonan@fullcycle\.com\.br', '/;

function arquivosFonte(dir) {
    return fs.readdirSync(dir, { withFileTypes: true }).flatMap((item) => {
        const caminho = path.join(dir, item.name);
        return item.isDirectory() ? arquivosFonte(caminho) : [caminho];
    });
}

describe('configuração', () => {
    it('código-fonte não contém segredos literais', () => {
        const comSegredo = arquivosFonte(SRC).filter((arquivo) => SEGREDOS_LITERAIS.test(fs.readFileSync(arquivo, 'utf8')));
        assert.deepEqual(comSegredo, []);
    });

    it('sem ambiente não há credencial nem provedor padrão', () => {
        const { loadSettings } = require('../src/config/settings');
        const settings = loadSettings({});
        assert.equal(settings.adminApiKey, '');
        assert.equal(settings.seedUserPassword, '');
        assert.equal(settings.paymentProvider, '');
        assert.equal(settings.paymentApiKey, '');
    });

    it('segredos são lidos do ambiente', () => {
        const { loadSettings } = require('../src/config/settings');
        const settings = loadSettings({ ADMIN_API_KEY: 'chave-teste', PAYMENT_GATEWAY_KEY: 'gateway-teste', PORT: '3100' });
        assert.equal(settings.adminApiKey, 'chave-teste');
        assert.equal(settings.paymentApiKey, 'gateway-teste');
        assert.equal(settings.port, 3100);
    });
});
