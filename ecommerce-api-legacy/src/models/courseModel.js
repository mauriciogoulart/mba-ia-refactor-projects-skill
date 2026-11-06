function createCourseModel(db) {
    return {
        findActiveById(id) {
            return db.get('SELECT id, title, price AS priceCents FROM courses WHERE id = ? AND active = 1', [id]);
        },
    };
}

module.exports = { createCourseModel };
