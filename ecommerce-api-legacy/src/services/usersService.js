'use strict';

function createUsersService(db, users) {
  return {
    async deleteUser(rawId) {
      if (!/^\d+$/.test(rawId) || Number(rawId) < 1 || !Number.isSafeInteger(Number(rawId))) throw Object.assign(new Error('Invalid user id'), { status: 400 });
      await db.runAsync('BEGIN IMMEDIATE TRANSACTION');
      try {
        const result = await users.deleteById(Number(rawId));
        if (!result.changes) throw Object.assign(new Error('Usuário não encontrado'), { status: 404 });
        await db.runAsync('COMMIT');
      } catch (error) {
        await db.runAsync('ROLLBACK').catch(() => {});
        throw error;
      }
    }
  };
}

module.exports = { createUsersService };
