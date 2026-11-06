const { PAYMENT_STATUS } = require('../config/constants');
const { AppError } = require('../utils/appError');

function createCheckoutService({
    db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentGateway, passwordService, logger,
}) {
    // Executa um passo de persistência; falha vira erro HTTP com a mensagem original da API.
    const step = async (mensagem, fn) => {
        try {
            return await fn();
        } catch (err) {
            logger.error(`checkout: ${mensagem}`, { error: err.message });
            throw new AppError(500, mensagem);
        }
    };

    async function findCourse(courseId) {
        try {
            return await courseModel.findActiveById(courseId);
        } catch (err) {
            // Contrato preservado: erro de banco na busca do curso responde 404 (F-019, residual).
            logger.error('checkout: falha ao buscar curso', { error: err.message });
            return null;
        }
    }

    async function checkout({ name, email, password, courseId, cardNumber }) {
        const course = await findCourse(courseId);
        if (!course) throw new AppError(404, 'Curso não encontrado');

        const existingUserId = await step('Erro DB', () => userModel.findIdByEmail(email));

        // O pagamento é decidido antes de qualquer gravação.
        const status = await paymentGateway.charge({ cardNumber, amountCents: course.priceCents });
        if (status === PAYMENT_STATUS.DENIED) throw new AppError(400, 'Pagamento recusado');

        const passwordHash = existingUserId
            ? null
            : await passwordService.hashPassword(password || passwordService.generateRandomPassword());

        const result = await db.transaction(async () => {
            const userId = existingUserId
                ?? await step('Erro ao criar usuário', () => userModel.create({ name, email, passwordHash }));
            const enrollmentId = await step('Erro Matrícula', () => enrollmentModel.create({ userId, courseId: course.id }));
            await step('Erro Pagamento', () => paymentModel.create({ enrollmentId, amountCents: course.priceCents, status }));
            await step('Erro Auditoria', () => auditLogModel.create(`Checkout curso ${course.id} por ${userId}`));
            return { userId, enrollmentId };
        });

        logger.info('checkout concluído', { userId: result.userId, courseId: course.id, enrollmentId: result.enrollmentId });
        return result.enrollmentId;
    }

    return { checkout };
}

module.exports = { createCheckoutService };
