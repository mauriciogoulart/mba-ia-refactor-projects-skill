const { PAYMENT_STATUS } = require('../config/constants');

// Valores monetários (courses.price, payments.amount) em centavos inteiros.
// enrollments.user_id não tem FK para preservar o comportamento atual de DELETE /api/users/:id.
const DDL = `
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
    price INTEGER NOT NULL,
    active INTEGER NOT NULL
);
CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL REFERENCES courses(id)
);
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id),
    amount INTEGER NOT NULL,
    status TEXT NOT NULL
);
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    action TEXT NOT NULL,
    created_at DATETIME NOT NULL
);
`;

async function initializeDatabase(db, { seedUserPasswordHash }) {
    await db.exec(DDL);
    await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', seedUserPasswordHash]);
    await db.run('INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)',
        ['Clean Architecture', 99700, 'Docker', 49700]);
    await db.run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    await db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 99700, ?)', [PAYMENT_STATUS.PAID]);
}

module.exports = { initializeDatabase };
