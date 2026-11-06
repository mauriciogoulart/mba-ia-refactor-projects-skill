function createPaymentModel(db) {
    return {
        create({ enrollmentId, amountCents, status }) {
            return db.run('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
                [enrollmentId, amountCents, status]);
        },
    };
}

module.exports = { createPaymentModel };
