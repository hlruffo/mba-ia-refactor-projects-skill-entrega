from flask import Blueprint, jsonify, request
from controllers.report_controller import ReportController

report_bp = Blueprint('reports', __name__)

@report_bp.get('/reports/summary')
def summary_report():
    return jsonify(ReportController.summary()), 200

@report_bp.get('/reports/user/<int:user_id>')
def user_report(user_id):
    return jsonify(ReportController.user_report(user_id)), 200

@report_bp.get('/categories')
def get_categories():
    return jsonify(ReportController.categories()), 200

@report_bp.post('/categories')
def create_category():
    body, status = ReportController.create_category(request.get_json(silent=True))
    return jsonify(body), status

@report_bp.put('/categories/<int:cat_id>')
def update_category(cat_id):
    return jsonify(ReportController.update_category(cat_id, request.get_json(silent=True))), 200

@report_bp.delete('/categories/<int:cat_id>')
def delete_category(cat_id):
    return jsonify(ReportController.delete_category(cat_id)), 200
