'use strict';

function createUsersRepository(db) {
  return {
    findByEmail(email) { return db.getAsync('SELECT id, name, email FROM users WHERE email = ?', [email]); },
    create({ name, email, passwordHash }) {
      return db.runAsync('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
    },
    deleteById(id) { return db.runAsync('DELETE FROM users WHERE id = ?', [id]); }
  };
}

module.exports = { createUsersRepository };
