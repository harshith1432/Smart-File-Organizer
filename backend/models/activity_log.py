from datetime import datetime
from backend.extensions import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # e.g., 'scanned', 'moved', 'deleted', 'rule_created'
    action = db.Column(db.String(100), nullable=False)
    
    # JSON or text details of the action
    details = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }
