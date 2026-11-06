// Logger em JSON por linha, com nível mínimo configurável.
// Nunca registre cartão completo, senha, token ou chave: passe apenas identificadores ou valores mascarados.
const LEVELS = { debug: 10, info: 20, warn: 30, error: 40 };

function createLogger(level = 'info') {
    const minimo = LEVELS[level] ?? LEVELS.info;

    const write = (nivel, msg, meta = {}) => {
        if (LEVELS[nivel] < minimo) return;
        const linha = JSON.stringify({ time: new Date().toISOString(), level: nivel, msg, ...meta });
        if (LEVELS[nivel] >= LEVELS.warn) process.stderr.write(`${linha}\n`);
        else process.stdout.write(`${linha}\n`);
    };

    return {
        debug: (msg, meta) => write('debug', msg, meta),
        info: (msg, meta) => write('info', msg, meta),
        warn: (msg, meta) => write('warn', msg, meta),
        error: (msg, meta) => write('error', msg, meta),
    };
}

const maskCard = (cardNumber) => `***${String(cardNumber).slice(-4)}`;

module.exports = { createLogger, maskCard };
