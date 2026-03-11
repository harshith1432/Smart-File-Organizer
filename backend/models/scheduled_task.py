from datetime import datetime
from backend.extensions import db

class ScheduledTask(db.Model):
    __tablename__ = 'scheduled_tasks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # e.g., 'daily_scan', 'weekly_cleanup'
    task_type = db.Column(db.String(100), nullable=False)
    
    # e.g., 'daily', 'weekly', 'monthly'
    schedule = db.Column(db.String(50), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'task_type': self.task_type,
            'schedule': self.schedule,
            'is_active': self.is_active,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None
        }
