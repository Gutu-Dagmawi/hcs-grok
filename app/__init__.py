from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import Config
from app.extensions import db, migrate
import os
from app.cli import clear_users_command

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
csrf = CSRFProtect()

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(Config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.patient import patient_bp
    
    # Register auth routes first (they don't have a prefix)
    app.register_blueprint(auth_bp)
    # Then register other routes
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(patient_bp)

    # Register CLI commands
    app.cli.add_command(clear_users_command)

    return app 