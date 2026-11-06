function createReportController({ reportService }) {
    return {
        async financialReport(req, res) {
            res.json(await reportService.getFinancialReport());
        },
    };
}

module.exports = { createReportController };
