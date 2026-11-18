const { MESSAGES } = require('../config/constants');
const { parseCheckoutRequest } = require('../validators/checkoutValidator');

function createCheckoutController({ checkoutService }) {
    return {
        async checkout(req, res) {
            const { enrollmentId } = await checkoutService.checkout(parseCheckoutRequest(req.body));
            res.status(200).json({ msg: MESSAGES.CHECKOUT_SUCCESS, enrollment_id: enrollmentId });
        },
    };
}

module.exports = { createCheckoutController };
