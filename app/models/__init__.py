from app import db, login_manager, bcrypt
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='department', lazy=True)
    indent_requests = db.relationship('IndentRequest', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum('indentor', 'hod', 'chairman', 'manager', 'admin'), nullable=False, default='indentor')
    designation = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    indent_requests = db.relationship('IndentRequest', backref='indentor', lazy=True, foreign_keys='IndentRequest.indentor_id')
    approvals = db.relationship('ApprovalLog', backref='approver', lazy=True)
    ratings = db.relationship('Rating', backref='rater', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name} ({self.role})>'


class IndentRequest(db.Model):
    __tablename__ = 'indent_requests'
    id = db.Column(db.Integer, primary_key=True)
    indent_number = db.Column(db.String(20), unique=True, nullable=False)
    indentor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    scheme_no = db.Column(db.String(50))

    # Event details
    event_type = db.Column(db.Enum('meeting', 'seminar', 'conference', 'training', 'other'), nullable=False)
    event_description = db.Column(db.String(255))
    venue = db.Column(db.String(200), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.String(50))
    number_of_persons = db.Column(db.Integer, nullable=False)
    special_instructions = db.Column(db.Text)

    # Service items (JSON-like stored as text, parsed in app)
    service_type_1 = db.Column(db.Boolean, default=False)  # Tea/Coffee with Snacks
    service_type_2 = db.Column(db.Boolean, default=False)  # Tea/Coffee with refreshment box
    service_type_3 = db.Column(db.Boolean, default=False)  # Fruit Juice/Cold Drink
    service_type_4 = db.Column(db.Enum('none', 'working', 'regular', 'special', 'executive'), default='none')
    service_quantity_1 = db.Column(db.Integer, default=0)
    service_quantity_2 = db.Column(db.Integer, default=0)
    service_quantity_3 = db.Column(db.Integer, default=0)
    service_quantity_4 = db.Column(db.Integer, default=0)
    service_time_1 = db.Column(db.String(50))
    service_time_2 = db.Column(db.String(50))
    service_time_3 = db.Column(db.String(50))
    service_time_4 = db.Column(db.String(50))

    # Status
    status = db.Column(
        db.Enum('draft', 'pending_hod', 'hod_approved', 'hod_rejected',
                'chairman_approved', 'chairman_rejected',
                'in_progress', 'completed'),
        default='pending_hod', nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    approvals = db.relationship('ApprovalLog', backref='indent', lazy=True, cascade='all, delete-orphan')
    rating = db.relationship('Rating', backref='indent', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<IndentRequest {self.indent_number}>'

    def get_status_display(self):
        status_map = {
            'draft': ('Draft', 'secondary'),
            'pending_hod': ('Pending HOD', 'warning'),
            'hod_approved': ('HOD Approved', 'info'),
            'hod_rejected': ('HOD Rejected', 'danger'),
            'chairman_approved': ('Chairman Approved', 'primary'),
            'chairman_rejected': ('Chairman Rejected', 'danger'),
            'in_progress': ('In Progress', 'info'),
            'completed': ('Completed', 'success'),
        }
        return status_map.get(self.status, ('Unknown', 'secondary'))

    def get_lunch_price(self):
        price_map = {
            'working': 90,
            'regular': 150,
            'special': 200,
            'executive': 275,
        }
        return price_map.get(self.service_type_4, 0)


class ApprovalLog(db.Model):
    __tablename__ = 'approval_logs'
    id = db.Column(db.Integer, primary_key=True)
    indent_id = db.Column(db.Integer, db.ForeignKey('indent_requests.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.Enum('hod', 'chairman', 'manager'), nullable=False)
    action = db.Column(db.Enum('approved', 'rejected', 'in_progress', 'completed'), nullable=False)
    remarks = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ApprovalLog {self.indent_id} by {self.approver_id}: {self.action}>'


class Rating(db.Model):
    __tablename__ = 'ratings'
    id = db.Column(db.Integer, primary_key=True)
    indent_id = db.Column(db.Integer, db.ForeignKey('indent_requests.id'), nullable=False, unique=True)
    rater_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    food_quality = db.Column(db.Integer, nullable=False)   # 1-5
    service_quality = db.Column(db.Integer, nullable=False)
    timeliness = db.Column(db.Integer, nullable=False)
    overall = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Rating for indent {self.indent_id}: {self.overall}/5>'
