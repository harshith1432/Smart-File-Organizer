from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend.extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    files = db.relationship('FileRecord', backref='owner', lazy=True)
    scan_history = db.relationship('ScanHistory', backref='owner', lazy=True)
    rules = db.relationship('OrganizationRule', backref='owner', lazy=True)
    duplicates = db.relationship('Duplicate', backref='owner', lazy=True)
    logs = db.relationship('ActivityLog', backref='owner', lazy=True)
    scheduled_tasks = db.relationship('ScheduledTask', backref='owner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
