const sqlite3 = require('sqlite3');

// Abre a conexão SQLite e expõe uma interface baseada em Promises (P-12).
function openDatabase(filename) {
    return new Promise((resolve, reject) => {
        const raw = new sqlite3.Database(filename, (err) => {
            if (err) return reject(err);
            resolve(wrap(raw));
        });
    });
}

function wrap(raw) {
    const db = {
        run(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.run(sql, params, function onRun(err) {
                    if (err) return reject(err);
                    resolve({ lastID: this.lastID, changes: this.changes });
                });
            });
        },
        get(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
            });
        },
        all(sql, params = []) {
            return new Promise((resolve, reject) => {
                raw.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
            });
        },
        exec(sql) {
            return new Promise((resolve, reject) => {
                raw.exec(sql, (err) => (err ? reject(err) : resolve()));
            });
        },
        close() {
            return new Promise((resolve, reject) => {
                raw.close((err) => (err ? reject(err) : resolve()));
            });
        },
    };

    // Transações serializadas: uma por vez sobre a conexão única, com ROLLBACK em qualquer falha (P-10).
    let queue = Promise.resolve();
    db.transaction = (work) => {
        const result = queue.then(async () => {
            await db.exec('BEGIN IMMEDIATE');
            try {
                const value = await work(db);
                await db.exec('COMMIT');
                return value;
            } catch (err) {
                await db.exec('ROLLBACK');
                throw err;
            }
        });
        queue = result.catch(() => {});
        return result;
    };

    return db;
}

module.exports = { openDatabase };
