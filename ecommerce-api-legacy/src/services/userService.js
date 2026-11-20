const { MESSAGES } = require('../config/constants');
const { AppError } = require('../errors/AppError');

function createUserService({ db, userModel, enrollmentModel, paymentModel }) {
    // Remove o usuário com matrículas e pagamentos na mesma transação (CT-04).
    async function deleteUser(userId) {
        await db.transaction(async () => {
            await paymentModel.deleteByUserId(userId);
            await enrollmentModel.deleteByUserId(userId);
            const removed = await userModel.deleteById(userId);
            if (removed === 0) throw new AppError(MESSAGES.USER_NOT_FOUND, 404);
        });
    }

    return { deleteUser };
}

module.exports = { createUserService };
