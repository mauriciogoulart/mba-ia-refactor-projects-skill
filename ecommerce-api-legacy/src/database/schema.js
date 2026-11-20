const crypto = require('node:crypto');
const { PAYMENT_STATUS } = require('../config/constants');

// DDL de criação (banco recriado a cada boot): integridade declarada e dinheiro em centavos (P-10, P-17).
const SCHEMA = `
    PRAGMA foreign_keys = ON;
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        pass TEXT NOT NULL
    );
    CREATE TABLE courses (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
        active INTEGER NOT NULL DEFAULT 1
    );
    CREATE TABLE enrollments (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        course_id INTEGER NOT NULL REFERENCES courses(id)
    );
    CREATE TABLE payments (
        id INTEGER PRIMARY KEY,
        enrollment_id INTEGER NOT NULL UNIQUE REFERENCES enrollments(id),
        amount_cents INTEGER NOT NULL,
        status TEXT NOT NULL
    );
    CREATE TABLE audit_logs (
        id INTEGER PRIMARY KEY,
        action TEXT NOT NULL,
        created_at DATETIME NOT NULL
    );
`;

async function createSchema(db) {
    await db.exec(SCHEMA);
}

// Dados de demonstração. A senha do usuário de seed vem da configuração; sem ela, usa um valor
// aleatório que nunca é exibido (não existe credencial padrão).
async function seedDatabase(db, { seedUserPassword, passwordService, logger }) {
    const password = seedUserPassword || crypto.randomBytes(24).toString('base64url');
    if (!seedUserPassword) logger.warn('SEED_USER_PASSWORD não definida: usuário de seed criado com senha aleatória');
    const passHash = await passwordService.hash(password);

    await db.transaction(async (tx) => {
        await tx.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', ['Leonan', 'leonan@fullcycle.com.br', passHash]);
        await tx.run('INSERT INTO courses (title, price_cents, active) VALUES (?, ?, 1), (?, ?, 1)', ['Clean Architecture', 99700, 'Docker', 49700]);
        await tx.run('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
        await tx.run('INSERT INTO payments (enrollment_id, amount_cents, status) VALUES (?, ?, ?)', [1, 99700, PAYMENT_STATUS.PAID]);
    });
}

module.exports = { createSchema, seedDatabase };
