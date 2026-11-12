'use strict';

function createFinancialReportService(repository) {
  return {
    async getReport() {
      return (await repository.findReport()).map(({ course, revenue, students_json }) => ({
        course, revenue, students: JSON.parse(students_json).filter(Boolean)
      }));
    }
  };
}

module.exports = { createFinancialReportService };
