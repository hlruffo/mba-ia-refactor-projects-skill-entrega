'use strict';

const { randomBytes, scrypt: scryptCallback } = require('node:crypto');
const { promisify } = require('node:util');
const scrypt = promisify(scryptCallback);

function validateCheckout(input) {
  const { usr, eml, pwd, c_id: courseId, card } = input || {};
  if (typeof usr !== 'string' || usr.trim().length < 1 || usr.trim().length > 100) throw Object.assign(new Error('Invalid name'), { status: 400 });
  if (typeof eml !== 'string' || eml.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(eml)) throw Object.assign(new Error('Invalid email'), { status: 400 });
  if (typeof pwd !== 'string' || pwd.length < 8 || pwd.length > 256) throw Object.assign(new Error('Invalid password'), { status: 400 });
  if (!Number.isSafeInteger(Number(courseId)) || Number(courseId) < 1) throw Object.assign(new Error('Invalid course id'), { status: 400 });
  if (typeof card !== 'string' || !/^\d{12,19}$/.test(card)) throw Object.assign(new Error('Invalid card'), { status: 400 });
  return { name: usr.trim(), email: eml.trim().toLowerCase(), password: pwd, courseId: Number(courseId), card };
}

function createCheckoutService({ db, users, courses, checkoutRepository }) {
  return {
    async checkout(rawInput) {
      const input = validateCheckout(rawInput);
      const course = await courses.findActiveById(input.courseId);
      if (!course) throw Object.assign(new Error('Curso não encontrado'), { status: 404 });
      if (!input.card.startsWith('4')) throw Object.assign(new Error('Pagamento recusado'), { status: 400 });

      const salt = randomBytes(16);
      const derivedKey = await scrypt(input.password, salt, 64);
      const passwordHash = `${salt.toString('hex')}:${derivedKey.toString('hex')}`;
      await db.runAsync('BEGIN IMMEDIATE TRANSACTION');
      try {
        let user = await users.findByEmail(input.email);
        if (!user) {
          const created = await users.create({ name: input.name, email: input.email, passwordHash });
          user = { id: created.lastID };
        }
        const enrollmentId = await checkoutRepository.createEnrollmentAndPayment({
          userId: user.id, courseId: course.id, amount: course.price
        });
        await db.runAsync('COMMIT');
        return { msg: 'Sucesso', enrollment_id: enrollmentId };
      } catch (error) {
        await db.runAsync('ROLLBACK').catch(() => {});
        throw error;
      }
    }
  };
}

module.exports = { createCheckoutService, validateCheckout };
