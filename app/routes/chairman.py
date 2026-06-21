from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import IndentRequest, ApprovalLog, db
from functools import wraps

chairman_bp = Blueprint('chairman', __name__)

def chairman_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'chairman':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return login_required(decorated)

@chairman_bp.route('/dashboard')
@chairman_required
def dashboard():
    requests = IndentRequest.query.filter(
        IndentRequest.status.in_(['hod_approved', 'chairman_approved',
                                   'chairman_rejected', 'in_progress', 'completed'])
    ).order_by(IndentRequest.created_at.desc()).all()
    pending = [r for r in requests if r.status == 'hod_approved']
    stats = {
        'total': len(requests),
        'pending': len(pending),
        'approved': sum(1 for r in requests if r.status == 'chairman_approved'),
        'rejected': sum(1 for r in requests if r.status == 'chairman_rejected'),
    }
    return render_template('chairman/dashboard.html', requests=requests, pending=pending, stats=stats)

@chairman_bp.route('/request/<int:id>', methods=['GET', 'POST'])
@chairman_required
def review_request(id):
    indent = IndentRequest.query.filter_by(id=id).first_or_404()
    logs = ApprovalLog.query.filter_by(indent_id=id).order_by(ApprovalLog.timestamp).all()
    if request.method == 'POST':
        action = request.form.get('action')
        remarks = request.form.get('remarks', '')
        if action == 'approve':
            indent.status = 'chairman_approved'
            log_action = 'approved'
            flash('Request approved and sent to Manager.', 'success')
        elif action == 'reject':
            indent.status = 'chairman_rejected'
            log_action = 'rejected'
            flash('Request rejected.', 'danger')
        else:
            flash('Invalid action.', 'danger')
            return redirect(url_for('chairman.review_request', id=id))
        log = ApprovalLog(indent_id=id, approver_id=current_user.id,
                          role='chairman', action=log_action, remarks=remarks)
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('chairman.dashboard'))
    return render_template('chairman/review_request.html', indent=indent, logs=logs)
