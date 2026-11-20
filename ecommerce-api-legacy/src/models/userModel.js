function createUserModel(db) {
    return {
        findByEmail(email) {
            return db.get('SELECT id, name, email, pass FROM users WHERE email = ?', [email]);
        },
        async create({ name, email, passHash }) {
            const { lastID } = await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passHash]);
            return lastID;
        },
        async deleteById(id) {
            const { changes } = await db.run('DELETE FROM users WHERE id = ?', [id]);
            return changes;
        },
    };
}

module.exports = { createUserModel };
