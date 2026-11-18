// Logger mínimo com níveis, em linhas JSON (P-15). Nunca receba cartão, senha, token ou chave.
const LEVELS = Object.freeze({ debug: 10, info: 20, warn: 30, error: 40 });

function createLogger(level = 'info', stream = process.stdout) {
    const threshold = LEVELS[level] || LEVELS.info;
    const write = (lvl, msg, fields = {}) => {
        if (LEVELS[lvl] < threshold) return;
        stream.write(`${JSON.stringify({ time: new Date().toISOString(), level: lvl, msg, ...fields })}\n`);
    };
    return {
        debug: (msg, fields) => write('debug', msg, fields),
        info: (msg, fields) => write('info', msg, fields),
        warn: (msg, fields) => write('warn', msg, fields),
        error: (msg, fields) => write('error', msg, fields),
    };
}

// Mantém apenas os 4 últimos dígitos do cartão.
const cardLast4 = (cardNumber) => String(cardNumber).slice(-4);

module.exports = { createLogger, cardLast4 };
