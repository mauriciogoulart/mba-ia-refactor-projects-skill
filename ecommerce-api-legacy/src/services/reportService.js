const { PAYMENT_STATUS } = require('../config/constants');
const { AppError } = require('../utils/appError');
const { centsToReais } = require('../utils/money');

function createReportService({ reportModel, logger }) {
    async function getFinancialReport() {
        let rows;
        try {
            rows = await reportModel.listCourseEnrollments();
        } catch (err) {
            logger.error('relatório: falha na consulta', { error: err.message });
            throw new AppError(500, 'Erro DB');
        }

        const byCourse = new Map();
        for (const row of rows) {
            if (!byCourse.has(row.courseId)) {
                byCourse.set(row.courseId, { course: row.courseTitle, revenueCents: 0, students: [] });
            }
            if (row.enrollmentId === null) continue;

            const item = byCourse.get(row.courseId);
            if (row.paymentStatus === PAYMENT_STATUS.PAID) item.revenueCents += row.amountCents;
            item.students.push({
                student: row.studentName ?? 'Unknown',
                paid: row.amountCents === null ? 0 : centsToReais(row.amountCents),
            });
        }

        return [...byCourse.values()].map(({ course, revenueCents, students }) => ({
            course,
            revenue: centsToReais(revenueCents),
            students,
        }));
    }

    return { getFinancialReport };
}

module.exports = { createReportService };
