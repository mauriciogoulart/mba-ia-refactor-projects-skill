const { AppError } = require('../utils/appError');

// Valida o corpo de POST /api/checkout e o converte para nomes internos.
// As chaves do payload (usr, eml, pwd, c_id, card) são contrato público e não mudam.
function validateCheckout(req, res, next) {
    const { usr, eml, pwd, c_id: courseId, card } = req.body;

    if (!usr || !eml || !courseId || !card) return next(new AppError(400, 'Bad Request'));
    // Tipos inválidos derrubavam o processo (F-008); agora resultam em 400.
    if (typeof card !== 'string' || (pwd && typeof pwd !== 'string')) return next(new AppError(400, 'Bad Request'));

    req.checkoutInput = { name: usr, email: eml, password: pwd || null, courseId, cardNumber: card };
    next();
}

module.exports = { validateCheckout };
