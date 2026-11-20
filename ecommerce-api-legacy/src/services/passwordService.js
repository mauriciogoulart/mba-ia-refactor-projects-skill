const crypto = require('node:crypto');
const { promisify } = require('node:util');

const scrypt = promisify(crypto.scrypt);
const KEY_LENGTH = 64;
const SALT_BYTES = 16;
const SCRYPT_PARAMS = Object.freeze({ N: 16384, r: 8, p: 1 });

// Hash de senha com KDF e salt aleatório (P-03), sem dependência externa.
// Formato armazenado: scrypt$N$r$p$<salt base64>$<hash base64>
function createPasswordService() {
    return {
        async hash(password) {
            const salt = crypto.randomBytes(SALT_BYTES);
            const { N, r, p } = SCRYPT_PARAMS;
            const key = await scrypt(String(password), salt, KEY_LENGTH, { N, r, p });
            return ['scrypt', N, r, p, salt.toString('base64'), key.toString('base64')].join('$');
        },
        async verify(password, stored) {
            if (typeof password !== 'string' || typeof stored !== 'string') return false;
            const parts = stored.split('$');
            if (parts.length !== 6 || parts[0] !== 'scrypt') return false;
            const [, N, r, p, saltB64, hashB64] = parts;
            const expected = Buffer.from(hashB64, 'base64');
            const key = await scrypt(password, Buffer.from(saltB64, 'base64'), expected.length, { N: Number(N), r: Number(r), p: Number(p) });
            return crypto.timingSafeEqual(key, expected);
        },
    };
}

module.exports = { createPasswordService };
