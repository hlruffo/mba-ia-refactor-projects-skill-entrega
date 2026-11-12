'use strict';

const sqlite3 = require('sqlite3').verbose();
const { randomBytes, scrypt: scryptCallback } = require('node:crypto');
const { promisify } = require('node:util');
const scrypt = promisify(scryptCallback);

function openDatabase(filename) {
  const db = new sqlite3.Database(filename);
  db.runAsync = (sql, params = []) => new Promise((resolve, reject) => {
    db.run(sql, params, function onRun(error) {
      if (error) return reject(error);
      resolve({ lastID: this.lastID, changes: this.changes });
    });
  });
  db.getAsync = promisify(db.get.bind(db));
  db.allAsync = promisify(db.all.bind(db));
  return db;
}

async function initializeDatabase(db) {
  await db.runAsync('PRAGMA foreign_keys = ON');
  await db.runAsync(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, pass TEXT NOT NULL
  )`);
  await db.runAsync(`CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL CHECK (price >= 0), active INTEGER NOT NULL DEFAULT 1
  )`);
  await db.runAsync(`CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER NOT NULL REFERENCES courses(id)
  )`);
  await db.runAsync(`CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY, enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    amount REAL NOT NULL, status TEXT NOT NULL
  )`);
  await db.runAsync(`CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY, action TEXT NOT NULL, created_at DATETIME NOT NULL DEFAULT (datetime('now'))
  )`);

  const existingUser = await db.getAsync('SELECT id FROM users LIMIT 1');
  if (!existingUser) {
    const salt = randomBytes(16);
    const hash = await scrypt(randomBytes(32), salt, 64);
    await db.runAsync('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
      'Leonan', 'leonan@example.test', `${salt.toString('hex')}:${hash.toString('hex')}`
    ]);
  }
  if (!await db.getAsync('SELECT id FROM courses LIMIT 1')) {
    await db.runAsync("INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
  }
  if (!await db.getAsync('SELECT id FROM enrollments LIMIT 1')) {
    await db.runAsync('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    const enrollment = await db.getAsync('SELECT id FROM enrollments WHERE user_id = 1 AND course_id = 1 ORDER BY id DESC LIMIT 1');
    await db.runAsync("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, 997.00, 'PAID')", [enrollment.id]);
  }
}

module.exports = { openDatabase, initializeDatabase };
