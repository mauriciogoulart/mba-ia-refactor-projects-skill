// F-012 (ARC-05): relatório assíncrono com agregação correta e erro propagado.
const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { createReportService } = require('../src/services/reportService');

const linha = (courseId, courseTitle, enrollmentId, studentName, amountCents, paymentStatus) => ({
    courseId, courseTitle, enrollmentId, studentName, amountCents, paymentStatus,
});

describe('reportService', () => {
    it('agrega receita paga por curso e preserva o formato da resposta', async () => {
        const reportModel = {
            listCourseEnrollments: async () => [
                linha(1, 'Clean Architecture', 1, 'Ana', 99700, 'PAID'),
                linha(1, 'Clean Architecture', 2, null, 99700, 'DENIED'),
                linha(2, 'Docker', null, null, null, null),
            ],
        };
        assert.deepEqual(await createReportService({ reportModel }).financialReport(), [
            { course: 'Clean Architecture', revenue: 997, students: [{ student: 'Ana', paid: 997 }, { student: 'Unknown', paid: 997 }] },
            { course: 'Docker', revenue: 0, students: [] },
        ]);
    });

    it('soma centavos sem erro de ponto flutuante', async () => {
        const reportModel = {
            listCourseEnrollments: async () => [linha(1, 'Curso', 1, 'Ana', 10, 'PAID'), linha(1, 'Curso', 2, 'Bia', 20, 'PAID')],
        };
        const [curso] = await createReportService({ reportModel }).financialReport();
        assert.equal(curso.revenue, 0.3);
    });

    it('propaga falha do banco como rejeição', async () => {
        const reportModel = { listCourseEnrollments: async () => { throw new Error('falha simulada'); } };
        await assert.rejects(createReportService({ reportModel }).financialReport(), /falha simulada/);
    });
});
