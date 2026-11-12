'use strict';

function createFinancialReportController(service) {
  return { async getReport(req, res, next) {
    try { res.json(await service.getReport()); } catch (error) { next(error); }
  } };
}

module.exports = { createFinancialReportController };
