'use strict';

function createCheckoutRepository(db) {
  return {
    async createEnrollmentAndPayment({ userId, courseId, amount }) {
      const enrollment = await db.runAsync('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
      await db.runAsync('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollment.lastID, amount, 'PAID']);
      await db.runAsync('INSERT INTO audit_logs (action) VALUES (?)', [`Checkout course ${courseId} by user ${userId}`]);
      return enrollment.lastID;
    }
  };
}

module.exports = { createCheckoutRepository };
