const express = require('express');
const { asyncHandler } = require('../middlewares/errorHandler');
const { validateCheckout } = require('../middlewares/validateCheckout');

function createRouter({ checkoutController, reportController, userController, checkoutRateLimiter }) {
    const router = express.Router();

    router.post('/api/checkout', checkoutRateLimiter, validateCheckout, asyncHandler(checkoutController.checkout));
    router.get('/api/admin/financial-report', asyncHandler(reportController.financialReport));
    router.delete('/api/users/:id', asyncHandler(userController.remove));

    return router;
}

module.exports = { createRouter };
