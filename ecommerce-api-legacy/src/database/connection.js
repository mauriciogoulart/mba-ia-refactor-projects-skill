const sqlite3 = require('sqlite3');

// Envolve a conexão sqlite3 em métodos baseados em Promise.
function createConnection(filename) {
    const db = new sqlite3.Database(filename);
    let filaTransacoes = Promise.resolve();

    const run = (sql, params = []) => new Promise((resolve, reject) => {
        db.run(sql, params, function onRun(err) {
            if (err) return reject(err);
            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });

    const get = (sql, params = []) => new Promise((resolve, reject) => {
        db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });

    const all = (sql, params = []) => new Promise((resolve, reject) => {
        db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });

    const exec = (sql) => new Promise((resolve, reject) => {
        db.exec(sql, (err) => (err ? reject(err) : resolve()));
    });

    // A conexão é única: transações são enfileiradas para não se intercalarem.
    const transaction = (fn) => {
        const execucao = filaTransacoes.then(async () => {
            await run('BEGIN');
            try {
                const resultado = await fn();
                await run('COMMIT');
                return resultado;
            } catch (err) {
                await run('ROLLBACK').catch(() => {});
                throw err;
            }
        });
        filaTransacoes = execucao.catch(() => {});
        return execucao;
    };

    return { run, get, all, exec, transaction };
}

module.exports = { createConnection };
