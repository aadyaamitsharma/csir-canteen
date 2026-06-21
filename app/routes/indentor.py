from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import IndentRequest, Department, Rating, ApprovalLog, db
from functools import wraps
from datetime import datetime, date
import random, string

indentor_bp = Blueprint('indentor', __name__)

def indentor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'indentor':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return login_required(decorated)

def generate_indent_number():
    year = datetime.now().year
    rand = ''.join(random.choices(string.digits, k=5))
    return f'CSIR-{year}-{rand}'

@indentor_bp.route('/dashboard')
@indentor_required
def dashboard():
    requests = IndentRequest.query.filter_by(indentor_id=current_user.id).order_by(IndentRequest.created_at.desc()).all()
    stats = {
        'total': len(requests),
        'pending': sum(1 for r in requests if r.status == 'pending_hod'),
        'approved': sum(1 for r in requests if r.status in ['chairman_approved', 'in_progress']),
        'completed': sum(1 for r in requests if r.status == 'completed'),
        'rejected': sum(1 for r in requests if 'rejected' in r.status),
    }
    return render_template('indentor/dashboard.html', requests=requests, stats=stats)

@indentor_bp.route('/create', methods=['GET', 'POST'])
@indentor_required
def create_indent():
    departments = Department.query.all()
    if request.method == 'POST':
        f = request.form
        try:
            indent = IndentRequest(
                indent_number=generate_indent_number(),
                indentor_id=current_user.id,
                department_id=int(f.get('department_id', current_user.department_id or 1)),
                scheme_no=f.get('scheme_no', ''),
                event_type=f.get('event_type', 'meeting'),
                event_description=f.get('event_description', ''),
                venue=f.get('venue', ''),
                event_date=datetime.strptime(f.get('event_date'), '%Y-%m-%d').date(),
                event_time=datetime.strptime(f.get('event_time'), '%H:%M').time(),
                duration=f.get('duration', ''),
                number_of_persons=int(f.get('number_of_persons', 1)),
                special_instructions=f.get('special_instructions', ''),
                service_type_1='service_1' in f,
                service_type_2='service_2' in f,
                service_type_3='service_3' in f,
                service_type_4=f.get('service_type_4', 'none'),
                service_quantity_1=int(f.get('qty_1', 0)),
                service_quantity_2=int(f.get('qty_2', 0)),
                service_quantity_3=int(f.get('qty_3', 0)),
                service_quantity_4=int(f.get('qty_4', 0)),
                service_time_1=f.get('time_1', ''),
                service_time_2=f.get('time_2', ''),
                service_time_3=f.get('time_3', ''),
                service_time_4=f.get('time_4', ''),
                status='pending_hod'
            )
            db.session.add(indent)
            db.session.commit()
            flash(f'Indent {indent.indent_number} submitted successfully!', 'success')
            return redirect(url_for('indentor.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating indent: {str(e)}', 'danger')
    return render_template('indentor/create_indent.html', departments=departments, today=date.today().isoformat())

@indentor_bp.route('/request/<int:id>')
@indentor_required
def view_request(id):
    indent = IndentRequest.query.filter_by(id=id, indentor_id=current_user.id).first_or_404()
    logs = ApprovalLog.query.filter_by(indent_id=id).order_by(ApprovalLog.timestamp).all()
    return render_template('indentor/view_request.html', indent=indent, logs=logs)

@indentor_bp.route('/rate/<int:id>', methods=['GET', 'POST'])
@indentor_required
def rate_service(id):
    indent = IndentRequest.query.filter_by(id=id, indentor_id=current_user.id, status='completed').first_or_404()
    if indent.rating:
        flash('You have already rated this service.', 'info')
        return redirect(url_for('indentor.view_request', id=id))
    if request.method == 'POST':
        f = request.form
        rating = Rating(
            indent_id=id,
            rater_id=current_user.id,
            food_quality=int(f.get('food_quality', 3)),
            service_quality=int(f.get('service_quality', 3)),
            timeliness=int(f.get('timeliness', 3)),
            overall=int(f.get('overall', 3)),
            feedback=f.get('feedback', '')
        )
        db.session.add(rating)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('indentor.view_request', id=id))
    return render_template('indentor/rate_service.html', indent=indent)
