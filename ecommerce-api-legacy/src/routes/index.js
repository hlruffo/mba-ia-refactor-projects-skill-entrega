'use strict';

const express = require('express');
const { createUsersRepository } = require('../repositories/usersRepository');
const { createCoursesRepository } = require('../repositories/coursesRepository');
const { createCheckoutRepository } = require('../repositories/checkoutRepository');
const { createFinancialReportRepository } = require('../repositories/financialReportRepository');
const { createCheckoutService } = require('../services/checkoutService');
const { createFinancialReportService } = require('../services/financialReportService');
const { createUsersService } = require('../services/usersService');
const { createCheckoutController } = require('../controllers/checkoutController');
const { createFinancialReportController } = require('../controllers/financialReportController');
const { createUsersController } = require('../controllers/usersController');
const { createAdminAuth } = require('../middleware/adminAuth');

function createApiRouter({ db, config }) {
  const router = express.Router();
  const users = createUsersRepository(db);
  const courses = createCoursesRepository(db);
  const checkoutRepository = createCheckoutRepository(db);
  const checkoutController = createCheckoutController(createCheckoutService({ db, users, courses, checkoutRepository }));
  const reportController = createFinancialReportController(createFinancialReportService(createFinancialReportRepository(db)));
  const usersController = createUsersController(createUsersService(db, users));

  router.post('/checkout', checkoutController.checkout);
  router.get('/admin/financial-report', createAdminAuth(config), reportController.getReport);
  router.delete('/users/:id', usersController.deleteUser);
  return router;
}

module.exports = { createApiRouter };
