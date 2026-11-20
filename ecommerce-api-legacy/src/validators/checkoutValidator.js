const { MESSAGES } = require('../config/constants');
const { AppError } = require('../errors/AppError');

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+$/;
const CARD_PATTERN = /^\d{12,19}$/;
const POSITIVE_INTEGER_PATTERN = /^[1-9]\d*$/;

const isFilledString = (value) => typeof value === 'string' && value.trim() !== '';
const isValidCourseId = (value) => (typeof value === 'number' || typeof value === 'string')
    && POSITIVE_INTEGER_PATTERN.test(String(value));

// Traduz o payload público (usr, eml, pwd, c_id, card) para os nomes internos.
function parseCheckoutRequest(body) {
    const { usr, eml, pwd, c_id: courseId, card } = body || {};
    const validPassword = pwd === undefined || pwd === null || typeof pwd === 'string';

    if (!isFilledString(usr) || !isFilledString(eml) || !EMAIL_PATTERN.test(eml)
        || !validPassword || !isValidCourseId(courseId)
        || typeof card !== 'string' || !CARD_PATTERN.test(card)) {
        throw new AppError(MESSAGES.BAD_REQUEST, 400);
    }

    return { name: usr, email: eml, password: pwd || '', courseId: Number(courseId), cardNumber: card };
}

module.exports = { parseCheckoutRequest };
