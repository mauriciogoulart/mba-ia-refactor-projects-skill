const { randomBytes, scrypt } = require('node:crypto');
const { promisify } = require('node:util');

const scryptAsync = promisify(scrypt);
const SALT_BYTES = 16;
const KEY_LENGTH = 64;

// Formato armazenado: scrypt$<salt hex>$<hash hex>
async function hashPassword(password) {
    const salt = randomBytes(SALT_BYTES);
    const derived = await scryptAsync(password, salt, KEY_LENGTH);
    return `scrypt$${salt.toString('hex')}$${derived.toString('hex')}`;
}

// Usada quando nenhuma senha é informada: nunca um valor fixo previsível.
const generateRandomPassword = () => randomBytes(24).toString('base64url');

module.exports = { hashPassword, generateRandomPassword };
