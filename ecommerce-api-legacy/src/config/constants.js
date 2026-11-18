const PAYMENT_STATUS = Object.freeze({ PAID: 'PAID', DENIED: 'DENIED' });

const MESSAGES = Object.freeze({
    BAD_REQUEST: 'Bad Request',
    COURSE_NOT_FOUND: 'Curso não encontrado',
    PAYMENT_DENIED: 'Pagamento recusado',
    UNAUTHORIZED: 'Não autorizado',
    INVALID_CREDENTIALS: 'Credenciais inválidas',
    USER_NOT_FOUND: 'Usuário não encontrado',
    USER_DELETED: 'Usuário deletado.',
    TOO_MANY_REQUESTS: 'Muitas requisições',
    INTERNAL_ERROR: 'Erro interno',
    CHECKOUT_SUCCESS: 'Sucesso',
});

const CENTS_PER_UNIT = 100;

module.exports = { PAYMENT_STATUS, MESSAGES, CENTS_PER_UNIT };
