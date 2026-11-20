const express = require('express');
const { loadSettings } = require('./config/settings');
const { openDatabase } = require('./database/connection');
const { createSchema, seedDatabase } = require('./database/schema');
const { createUserModel } = require('./models/userModel');
const { createCourseModel } = require('./models/courseModel');
const { createEnrollmentModel } = require('./models/enrollmentModel');
const { createPaymentModel } = require('./models/paymentModel');
const { createAuditLogModel } = require('./models/auditLogModel');
const { createReportModel } = require('./models/reportModel');
const { createPasswordService } = require('./services/passwordService');
const { createPaymentGateway } = require('./services/payment/gatewayFactory');
const { createCheckoutService } = require('./services/checkoutService');
const { createReportService } = require('./services/reportService');
const { createUserService } = require('./services/userService');
const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');
const { createRequireAdmin } = require('./middlewares/requireAdmin');
const { createErrorHandler } = require('./middlewares/errorHandler');
const { createRateLimiter } = require('./middlewares/rateLimiter');
const { securityHeaders } = require('./middlewares/securityHeaders');
const { registerRoutes } = require('./routes');
const { createLogger } = require('./utils/logger');

// Composition root: único ponto que cria a infraestrutura e injeta as dependências.
async function createApplication(settings = loadSettings(), logger = createLogger(settings.logLevel)) {
    const db = await openDatabase(settings.databaseFile);
    const passwordService = createPasswordService();
    await createSchema(db);
    await seedDatabase(db, { seedUserPassword: settings.seedUserPassword, passwordService, logger });

    const userModel = createUserModel(db);
    const courseModel = createCourseModel(db);
    const enrollmentModel = createEnrollmentModel(db);
    const paymentModel = createPaymentModel(db);
    const auditLogModel = createAuditLogModel(db);
    const reportModel = createReportModel(db);
    const paymentGateway = createPaymentGateway({ settings, logger });

    const checkoutService = createCheckoutService({
        db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentGateway, passwordService, logger,
    });
    const reportService = createReportService({ reportModel });
    const userService = createUserService({ db, userModel, enrollmentModel, paymentModel });

    const app = express();
    app.disable('x-powered-by');
    app.use(securityHeaders);
    app.use(express.json());
    registerRoutes(app, {
        checkoutController: createCheckoutController({ checkoutService }),
        reportController: createReportController({ reportService }),
        userController: createUserController({ userService }),
        requireAdmin: createRequireAdmin({ adminApiKey: settings.adminApiKey }),
        checkoutRateLimiter: createRateLimiter(settings.checkoutRateLimit),
    });
    app.use(createErrorHandler({ logger }));

    if (!settings.adminApiKey) logger.warn('ADMIN_API_KEY não definida: rotas administrativas negam todas as requisições');
    return { app, db };
}

async function start() {
    const settings = loadSettings();
    const logger = createLogger(settings.logLevel);
    try {
        const { app } = await createApplication(settings, logger);
        app.listen(settings.port, () => logger.info(`LMS API rodando na porta ${settings.port}`));
    } catch (err) {
        logger.error('falha ao iniciar a aplicação', { error: err.message });
        process.exit(1);
    }
}

if (require.main === module) start();

module.exports = { createApplication };
