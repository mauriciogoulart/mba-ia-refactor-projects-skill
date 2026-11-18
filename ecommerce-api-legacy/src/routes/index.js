const { asyncHandler } = require('../utils/asyncHandler');

function registerRoutes(app, { checkoutController, reportController, userController, requireAdmin, checkoutRateLimiter }) {
    app.post('/api/checkout', checkoutRateLimiter, asyncHandler(checkoutController.checkout));
    app.get('/api/admin/financial-report', requireAdmin, asyncHandler(reportController.financialReport));
    app.delete('/api/users/:id', requireAdmin, asyncHandler(userController.remove));
}

module.exports = { registerRoutes };
