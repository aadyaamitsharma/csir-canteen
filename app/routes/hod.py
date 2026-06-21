from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import IndentRequest, ApprovalLog, db
from functools import wraps

hod_bp = Blueprint('hod', __name__)

def hod_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'hod':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return login_required(decorated)

@hod_bp.route('/dashboard')
@hod_required
def dashboard():
    dept_id = current_user.department_id
    requests = IndentRequest.query.filter(
        IndentRequest.department_id == dept_id,
        IndentRequest.status.in_(['pending_hod', 'hod_approved', 'hod_rejected',
                                   'chairman_approved', 'chairman_rejected',
                                   'in_progress', 'completed'])
    ).order_by(IndentRequest.created_at.desc()).all()
    pending = [r for r in requests if r.status == 'pending_hod']
    stats = {
        'total': len(requests),
        'pending': len(pending),
        'approved': sum(1 for r in requests if r.status == 'hod_approved'),
        'rejected': sum(1 for r in requests if r.status == 'hod_rejected'),
    }
    return render_template('hod/dashboard.html', requests=requests, pending=pending, stats=stats)

@hod_bp.route('/request/<int:id>', methods=['GET', 'POST'])
@hod_required
def review_request(id):
    indent = IndentRequest.query.filter_by(id=id).first_or_404()
    if indent.department_id != current_user.department_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('hod.dashboard'))
    logs = ApprovalLog.query.filter_by(indent_id=id).order_by(ApprovalLog.timestamp).all()
    if request.method == 'POST':
        action = request.form.get('action')
        remarks = request.form.get('remarks', '')
        if action == 'approve':
            indent.status = 'hod_approved'
            log_action = 'approved'
            flash('Request approved and sent to Chairman.', 'success')
        elif action == 'reject':
            indent.status = 'hod_rejected'
            log_action = 'rejected'
            flash('Request rejected.', 'danger')
        else:
            flash('Invalid action.', 'danger')
            return redirect(url_for('hod.review_request', id=id))
        log = ApprovalLog(indent_id=id, approver_id=current_user.id,
                          role='hod', action=log_action, remarks=remarks)
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('hod.dashboard'))
    return render_template('hod/review_request.html', indent=indent, logs=logs)
