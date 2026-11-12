'use strict';

function createCheckoutController(service) {
  return { async checkout(req, res, next) {
    try { res.status(200).json(await service.checkout(req.body)); } catch (error) { next(error); }
  } };
}

module.exports = { createCheckoutController };
