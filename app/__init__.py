from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.routes.auth import auth_bp
    from app.routes.indentor import indentor_bp
    from app.routes.hod import hod_bp
    from app.routes.chairman import chairman_bp
    from app.routes.manager import manager_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.print_route import print_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(indentor_bp, url_prefix='/indentor')
    app.register_blueprint(hod_bp, url_prefix='/hod')
    app.register_blueprint(chairman_bp, url_prefix='/chairman')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(print_bp)

    return app
