function createPaymentModel(db) {
    return {
        async create({ enrollmentId, amountCents, status }) {
            const { lastID } = await db.run(
                'INSERT INTO payments (enrollment_id, amount_cents, status) VALUES (?, ?, ?)',
                [enrollmentId, amountCents, status],
            );
            return lastID;
        },
        async deleteByUserId(userId) {
            const { changes } = await db.run(
                'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
                [userId],
            );
            return changes;
        },
    };
}

module.exports = { createPaymentModel };
