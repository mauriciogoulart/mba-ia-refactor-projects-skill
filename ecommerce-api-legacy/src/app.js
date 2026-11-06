// Composition root: cria a infraestrutura, injeta as dependências e inicia o servidor.
const express = require('express');
const settings = require('./config/settings');
const { createLogger } = require('./utils/logger');
const { createConnection } = require('./database/connection');
const { initializeDatabase } = require('./database/schema');
const { createUserModel } = require('./models/userModel');
const { createCourseModel } = require('./models/courseModel');
const { createEnrollmentModel } = require('./models/enrollmentModel');
const { createPaymentModel } = require('./models/paymentModel');
const { createAuditLogModel } = require('./models/auditLogModel');
const { createReportModel } = require('./models/reportModel');
const passwordService = require('./services/passwordService');
const { createSimulatedPaymentGateway } = require('./services/paymentGateway');
const { createCheckoutService } = require('./services/checkoutService');
const { createReportService } = require('./services/reportService');
const { createCheckoutController } = require('./controllers/checkoutController');
const { createReportController } = require('./controllers/reportController');
const { createUserController } = require('./controllers/userController');
const { createRouter } = require('./routes');
const { createErrorHandler } = require('./middlewares/errorHandler');
const { securityHeaders } = require('./middlewares/securityHeaders');
const { createRateLimiter } = require('./middlewares/rateLimit');

async function createApp({ config, logger }) {
    const db = createConnection(config.databaseFile);
    const seedPassword = config.seedUserPassword || passwordService.generateRandomPassword();
    await initializeDatabase(db, { seedUserPasswordHash: await passwordService.hashPassword(seedPassword) });

    const userModel = createUserModel(db);
    const checkoutService = createCheckoutService({
        db,
        userModel,
        courseModel: createCourseModel(db),
        enrollmentModel: createEnrollmentModel(db),
        paymentModel: createPaymentModel(db),
        auditLogModel: createAuditLogModel(db),
        paymentGateway: createSimulatedPaymentGateway({ logger }),
        passwordService,
        logger,
    });
    const reportService = createReportService({ reportModel: createReportModel(db), logger });

    const app = express();
    app.disable('x-powered-by');
    app.use(securityHeaders);
    app.use(express.json({ limit: config.jsonBodyLimit }));
    app.use(createRouter({
        checkoutController: createCheckoutController({ checkoutService }),
        reportController: createReportController({ reportService }),
        userController: createUserController({ userModel, logger }),
        checkoutRateLimiter: createRateLimiter(config.checkoutRateLimit),
    }));
    app.use(createErrorHandler(logger));
    return app;
}

async function start() {
    const logger = createLogger(settings.logLevel);
    try {
        const app = await createApp({ config: settings, logger });
        app.listen(settings.port, () => logger.info(`LMS API rodando na porta ${settings.port}`));
    } catch (err) {
        logger.error('falha ao iniciar a aplicação', { error: err.message, stack: err.stack });
        process.exitCode = 1;
    }
}

if (require.main === module) start();

module.exports = { createApp };
