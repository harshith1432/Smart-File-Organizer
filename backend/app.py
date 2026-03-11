import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Load environment variables
load_dotenv()

from backend.extensions import db, login_manager, jwt, scheduler

def create_app():
    app = Flask(__name__, 
                template_folder="../frontend/templates", 
                static_folder="../frontend/static")

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-jwt-key')

    # Security configuration to handle PostgreSQL Neon with SSL
    if app.config['SQLALCHEMY_DATABASE_URI'] and app.config['SQLALCHEMY_DATABASE_URI'].startswith("postgres://"):
        app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace("postgres://", "postgresql://", 1)

    # Initialize Extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    jwt.init_app(app)
    CORS(app)

    # Flask-Login User Loader
    from backend.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and Register Blueprints
    from backend.routes.auth_routes import auth_bp
    from backend.routes.scanner_routes import scanner_bp
    from backend.routes.organizer_routes import organizer_bp
    from backend.routes.analytics_routes import analytics_bp
    from backend.routes.scheduler_routes import scheduler_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(scanner_bp, url_prefix='/api/scan')
    app.register_blueprint(organizer_bp, url_prefix='/api/organizer')
    app.register_blueprint(analytics_bp, url_prefix='/api/stats')
    app.register_blueprint(scheduler_bp, url_prefix='/api/scheduler')

    # Base Routes for UI Navigation
    @app.route('/')
    @app.route('/dashboard')
    def index():
        return render_template('dashboard.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/signup')
    def signup_page():
        return render_template('signup.html')

    @app.route('/scanner')
    def scanner_page():
        return render_template('scanner.html')

    @app.route('/organizer')
    def organizer_page():
        return render_template('organizer.html')

    @app.route('/duplicates')
    def duplicates_page():
        return render_template('duplicate_finder.html')

    @app.route('/large-files')
    def large_files_page():
        return render_template('large_files.html')

    @app.route('/rules')
    def rules_page():
        return render_template('rules.html')

    @app.route('/logs')
    def logs_page():
        return render_template('logs.html')

    @app.route('/settings')
    def settings_page():
        return render_template('settings.html')

    # Start the scheduler
    if not scheduler.running:
        scheduler.start()

    with app.app_context():
        # Import all models to ensure they are registered with SQLAlchemy
        from backend.models import __init__
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
