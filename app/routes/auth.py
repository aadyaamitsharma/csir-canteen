from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

ROLE_REDIRECT = {
    'indentor': 'indentor.dashboard',
    'hod': 'hod.dashboard',
    'chairman': 'chairman.dashboard',
    'manager': 'manager.dashboard',
    'admin': 'admin.dashboard',
}

@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for(ROLE_REDIRECT.get(current_user.role, 'auth.login')))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for(ROLE_REDIRECT.get(current_user.role, 'auth.login')))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=True)
            user.last_login = datetime.utcnow()
            db.session.commit()
            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for(ROLE_REDIRECT.get(user.role, 'auth.login')))
        flash('Invalid email or password. Please try again.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.designation = request.form.get('designation', current_user.designation)
        new_pass = request.form.get('new_password', '').strip()
        if new_pass:
            if current_user.check_password(request.form.get('current_password', '')):
                current_user.set_password(new_pass)
                flash('Password updated successfully.', 'success')
            else:
                flash('Current password is incorrect.', 'danger')
                return redirect(url_for('auth.profile'))
        db.session.commit()
        flash('Profile updated successfully.', 'success')
    return render_template('auth/profile.html')
