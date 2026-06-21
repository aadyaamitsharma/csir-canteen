from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import User, Department, IndentRequest, Rating, ApprovalLog, db
from functools import wraps
from datetime import datetime
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return login_required(decorated)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    total_users = User.query.count()
    total_requests = IndentRequest.query.count()
    total_depts = Department.query.count()
    avg_rating = db.session.query(func.avg(Rating.overall)).scalar() or 0
    recent_requests = IndentRequest.query.order_by(IndentRequest.created_at.desc()).limit(10).all()
    stats = {
        'total_users': total_users,
        'total_requests': total_requests,
        'total_depts': total_depts,
        'avg_rating': round(float(avg_rating), 1),
        'pending': IndentRequest.query.filter_by(status='pending_hod').count(),
        'completed': IndentRequest.query.filter_by(status='completed').count(),
    }
    return render_template('admin/dashboard.html', stats=stats, recent_requests=recent_requests)

# ---- USER MANAGEMENT ----
@admin_bp.route('/users')
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    departments = Department.query.all()
    return render_template('admin/users.html', users=all_users, departments=departments)

@admin_bp.route('/users/create', methods=['POST'])
@admin_required
def create_user():
    f = request.form
    if User.query.filter_by(email=f.get('email')).first():
        flash('Email already exists.', 'danger')
        return redirect(url_for('admin.users'))
    user = User(
        name=f.get('name'),
        email=f.get('email'),
        employee_id=f.get('employee_id'),
        role=f.get('role'),
        designation=f.get('designation'),
        phone=f.get('phone'),
        department_id=int(f.get('department_id')) if f.get('department_id') else None,
    )
    user.set_password(f.get('password', 'csir@1234'))
    db.session.add(user)
    db.session.commit()
    flash(f'User {user.name} created successfully!', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/edit/<int:id>', methods=['POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    f = request.form
    user.name = f.get('name', user.name)
    user.email = f.get('email', user.email)
    user.employee_id = f.get('employee_id', user.employee_id)
    user.role = f.get('role', user.role)
    user.designation = f.get('designation', user.designation)
    user.phone = f.get('phone', user.phone)
    user.department_id = int(f.get('department_id')) if f.get('department_id') else None
    user.is_active = 'is_active' in f
    if f.get('password'):
        user.set_password(f.get('password'))
    db.session.commit()
    flash(f'User {user.name} updated.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash("You cannot delete yourself.", 'danger')
        return redirect(url_for('admin.users'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('admin.users'))

# ---- DEPARTMENT MANAGEMENT ----
@admin_bp.route('/departments')
@admin_required
def departments():
    depts = Department.query.all()
    return render_template('admin/departments.html', departments=depts)

@admin_bp.route('/departments/create', methods=['POST'])
@admin_required
def create_department():
    dept = Department(name=request.form.get('name'), code=request.form.get('code'))
    db.session.add(dept)
    db.session.commit()
    flash('Department created.', 'success')
    return redirect(url_for('admin.departments'))

@admin_bp.route('/departments/delete/<int:id>', methods=['POST'])
@admin_required
def delete_department(id):
    dept = Department.query.get_or_404(id)
    db.session.delete(dept)
    db.session.commit()
    flash('Department deleted.', 'success')
    return redirect(url_for('admin.departments'))

# ---- REPORTS ----
@admin_bp.route('/reports')
@admin_required
def reports():
    all_requests = IndentRequest.query.order_by(IndentRequest.created_at.desc()).all()
    return render_template('admin/reports.html', requests=all_requests)

# ---- ANALYTICS DATA ----
@admin_bp.route('/analytics')
@admin_required
def analytics():
    return render_template('admin/analytics.html')

@admin_bp.route('/analytics/data')
@admin_required
def analytics_data():
    # Requests per department
    dept_data = db.session.query(
        Department.name, func.count(IndentRequest.id)
    ).join(IndentRequest, Department.id == IndentRequest.department_id, isouter=True
    ).group_by(Department.name).all()

    # Status breakdown
    status_data = db.session.query(
        IndentRequest.status, func.count(IndentRequest.id)
    ).group_by(IndentRequest.status).all()

    # Monthly requests (last 6 months)
    monthly_data = db.session.query(
        func.month(IndentRequest.created_at).label('month'),
        func.year(IndentRequest.created_at).label('year'),
        func.count(IndentRequest.id)
    ).group_by('year', 'month').order_by('year', 'month').limit(12).all()

    # Average ratings
    avg_ratings = db.session.query(
        func.avg(Rating.food_quality),
        func.avg(Rating.service_quality),
        func.avg(Rating.timeliness),
        func.avg(Rating.overall)
    ).first()

    return jsonify({
        'departments': {'labels': [d[0] for d in dept_data], 'data': [d[1] for d in dept_data]},
        'status': {'labels': [s[0] for s in status_data], 'data': [s[1] for s in status_data]},
        'monthly': {
            'labels': [f"{m[1]}-{m[0]:02d}" if isinstance(m[0], int) else str(m) for m in monthly_data],
            'data': [m[2] for m in monthly_data]
        },
        'ratings': {
            'food': round(float(avg_ratings[0] or 0), 2),
            'service': round(float(avg_ratings[1] or 0), 2),
            'timeliness': round(float(avg_ratings[2] or 0), 2),
            'overall': round(float(avg_ratings[3] or 0), 2),
        }
    })
