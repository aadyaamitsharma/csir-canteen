from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import IndentRequest, ApprovalLog, db
from functools import wraps

manager_bp = Blueprint('manager', __name__)

def manager_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'manager':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return login_required(decorated)

@manager_bp.route('/dashboard')
@manager_required
def dashboard():
    requests = IndentRequest.query.filter(
        IndentRequest.status.in_(['chairman_approved', 'in_progress', 'completed'])
    ).order_by(IndentRequest.created_at.desc()).all()
    stats = {
        'total': len(requests),
        'pending': sum(1 for r in requests if r.status == 'chairman_approved'),
        'in_progress': sum(1 for r in requests if r.status == 'in_progress'),
        'completed': sum(1 for r in requests if r.status == 'completed'),
    }
    return render_template('manager/dashboard.html', requests=requests, stats=stats)

@manager_bp.route('/request/<int:id>', methods=['GET', 'POST'])
@manager_required
def manage_request(id):
    indent = IndentRequest.query.filter_by(id=id).first_or_404()
    logs = ApprovalLog.query.filter_by(indent_id=id).order_by(ApprovalLog.timestamp).all()
    if request.method == 'POST':
        action = request.form.get('action')
        remarks = request.form.get('remarks', '')
        if action == 'in_progress':
            indent.status = 'in_progress'
            log_action = 'in_progress'
            flash('Request marked as In Progress.', 'info')
        elif action == 'completed':
            indent.status = 'completed'
            log_action = 'completed'
            flash('Request marked as Completed.', 'success')
        else:
            flash('Invalid action.', 'danger')
            return redirect(url_for('manager.manage_request', id=id))
        log = ApprovalLog(indent_id=id, approver_id=current_user.id,
                          role='manager', action=log_action, remarks=remarks)
        db.session.add(log)
        db.session.commit()
        return redirect(url_for('manager.dashboard'))
    return render_template('manager/manage_request.html', indent=indent, logs=logs)
