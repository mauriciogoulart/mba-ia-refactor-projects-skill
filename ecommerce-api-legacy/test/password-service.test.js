// F-005 (SEC-06): senha protegida por KDF com salt, sem colisão por prefixo.
const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { createPasswordService } = require('../src/services/passwordService');

const passwordService = createPasswordService();

describe('hash de senha', () => {
    it('usa scrypt com salt aleatório e não expõe a senha', async () => {
        const [a, b] = await Promise.all([passwordService.hash('senhaforte'), passwordService.hash('senhaforte')]);
        assert.match(a, /^scrypt\$/);
        assert.notEqual(a, b);
        assert.ok(!a.includes(Buffer.from('senhaforte').toString('base64')));
    });

    it('aceita somente a senha exata', async () => {
        const hash = await passwordService.hash('senhaforte');
        assert.equal(await passwordService.verify('senhaforte', hash), true);
        assert.equal(await passwordService.verify('senhafraca', hash), false);
        assert.equal(await passwordService.verify('', hash), false);
        assert.equal(await passwordService.verify(undefined, hash), false);
    });
});
