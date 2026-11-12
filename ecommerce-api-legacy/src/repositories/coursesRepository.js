'use strict';

function createCoursesRepository(db) {
  return { findActiveById(id) { return db.getAsync('SELECT id, title, price FROM courses WHERE id = ? AND active = 1', [id]); } };
}

module.exports = { createCoursesRepository };
