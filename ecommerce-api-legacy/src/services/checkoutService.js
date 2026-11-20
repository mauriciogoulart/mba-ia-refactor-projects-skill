const crypto = require('node:crypto');
const { MESSAGES, PAYMENT_STATUS } = require('../config/constants');
const { AppError } = require('../errors/AppError');
const { cardLast4 } = require('../utils/logger');

function createCheckoutService({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentGateway, passwordService, logger }) {
    // E-mail já cadastrado exige a senha da conta antes de qualquer cobrança ou escrita (CT-03).
    async function assertAccountOwner(user, password) {
        const valid = await passwordService.verify(password, user.pass);
        if (!valid) throw new AppError(MESSAGES.INVALID_CREDENTIALS, 401);
    }

    // Sem senha informada, a conta nasce com senha aleatória não divulgada (não há senha padrão).
    function hashNewUserPassword(password) {
        return passwordService.hash(password || crypto.randomBytes(24).toString('base64url'));
    }

    async function checkout({ name, email, password, courseId, cardNumber }) {
        const course = await courseModel.findActiveById(courseId);
        if (!course) throw new AppError(MESSAGES.COURSE_NOT_FOUND, 404);

        const existingUser = await userModel.findByEmail(email);
        if (existingUser) await assertAccountOwner(existingUser, password);

        const charge = await paymentGateway.charge({ cardNumber, amountCents: course.priceCents });
        if (charge.status !== PAYMENT_STATUS.PAID) throw new AppError(MESSAGES.PAYMENT_DENIED, 400);

        const newUserHash = existingUser ? null : await hashNewUserPassword(password);

        const { userId, enrollmentId } = await db.transaction(async () => {
            const buyerId = existingUser
                ? existingUser.id
                : await userModel.create({ name, email, passHash: newUserHash });
            const newEnrollmentId = await enrollmentModel.create({ userId: buyerId, courseId: course.id });
            await paymentModel.create({ enrollmentId: newEnrollmentId, amountCents: course.priceCents, status: charge.status });
            await auditLogModel.create(`Checkout curso ${course.id} por ${buyerId}`);
            return { userId: buyerId, enrollmentId: newEnrollmentId };
        });

        logger.info('checkout concluído', { userId, courseId: course.id, enrollmentId, last4: cardLast4(cardNumber) });
        return { enrollmentId };
    }

    return { checkout };
}

module.exports = { createCheckoutService };
