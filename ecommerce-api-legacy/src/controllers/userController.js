const { MESSAGES } = require('../config/constants');
const { AppError } = require('../errors/AppError');

const USER_ID_PATTERN = /^[1-9]\d*$/;

function createUserController({ userService }) {
    return {
        async remove(req, res) {
            if (!USER_ID_PATTERN.test(req.params.id)) throw new AppError(MESSAGES.USER_NOT_FOUND, 404);
            await userService.deleteUser(Number(req.params.id));
            res.send(MESSAGES.USER_DELETED);
        },
    };
}

module.exports = { createUserController };
