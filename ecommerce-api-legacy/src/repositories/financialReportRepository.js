'use strict';

function createFinancialReportRepository(db) {
  return {
    findReport() {
      return db.allAsync(`SELECT c.title AS course,
          COALESCE(SUM(CASE WHEN p.status = 'PAID' THEN p.amount ELSE 0 END), 0) AS revenue,
          COALESCE(json_group_array(CASE WHEN e.id IS NOT NULL THEN json_object(
            'student', u.name, 'paid', CASE WHEN p.status = 'PAID' THEN p.amount ELSE 0 END
          ) END), '[]') AS students_json
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u ON u.id = e.user_id
        LEFT JOIN payments p ON p.enrollment_id = e.id
        GROUP BY c.id, c.title ORDER BY c.id`);
    }
  };
}

module.exports = { createFinancialReportRepository };
