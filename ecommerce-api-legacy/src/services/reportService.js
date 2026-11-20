const { CENTS_PER_UNIT, PAYMENT_STATUS } = require('../config/constants');

const UNKNOWN_STUDENT = 'Unknown';
const toUnits = (cents) => cents / CENTS_PER_UNIT;

function createReportService({ reportModel }) {
    async function financialReport() {
        const rows = await reportModel.listCourseEnrollments();
        const courses = new Map();

        for (const row of rows) {
            if (!courses.has(row.courseId)) {
                courses.set(row.courseId, { course: row.courseTitle, revenueCents: 0, students: [] });
            }
            if (row.enrollmentId === null) continue;

            const entry = courses.get(row.courseId);
            const amountCents = row.amountCents || 0;
            if (row.paymentStatus === PAYMENT_STATUS.PAID) entry.revenueCents += amountCents;
            entry.students.push({ student: row.studentName || UNKNOWN_STUDENT, paid: toUnits(amountCents) });
        }

        return [...courses.values()].map(({ course, revenueCents, students }) => ({
            course,
            revenue: toUnits(revenueCents),
            students,
        }));
    }

    return { financialReport };
}

module.exports = { createReportService };
