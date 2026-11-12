'use strict';

function createUsersController(service) {
  return { async deleteUser(req, res, next) {
    try { await service.deleteUser(req.params.id); res.status(200).send('Usuário deletado.'); } catch (error) { next(error); }
  } };
}

module.exports = { createUsersController };
