from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import IndentRequest, User, Department

api_bp = Blueprint('api', __name__)

@api_bp.route('/requests/status/<int:id>')
@login_required
def request_status(id):
    indent = IndentRequest.query.get_or_404(id)
    label, color = indent.get_status_display()
    return jsonify({'status': indent.status, 'label': label, 'color': color})

@api_bp.route('/users/search')
@login_required
def search_users():
    if current_user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403
    q = request.args.get('q', '')
    users = User.query.filter(User.name.ilike(f'%{q}%')).limit(10).all()
    return jsonify([{'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role} for u in users])

@api_bp.route('/notifications')
@login_required
def notifications():
    count = 0
    if current_user.role == 'hod':
        count = IndentRequest.query.filter_by(
            department_id=current_user.department_id, status='pending_hod').count()
    elif current_user.role == 'chairman':
        count = IndentRequest.query.filter_by(status='hod_approved').count()
    elif current_user.role == 'manager':
        count = IndentRequest.query.filter_by(status='chairman_approved').count()
    elif current_user.role == 'indentor':
        count = IndentRequest.query.filter(
            IndentRequest.indentor_id == current_user.id,
            IndentRequest.status == 'completed',
            ~IndentRequest.rating.has()
        ).count()
    return jsonify({'count': count})
