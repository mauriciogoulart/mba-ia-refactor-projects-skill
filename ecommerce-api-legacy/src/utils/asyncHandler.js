// Encaminha rejeições de handlers assíncronos ao tratamento central de erros.
const asyncHandler = (handler) => (req, res, next) => Promise.resolve(handler(req, res, next)).catch(next);

module.exports = { asyncHandler };
