from datetime import datetime
from backend.extensions import db

class OrganizationRule(db.Model):
    __tablename__ = 'organization_rules'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    name = db.Column(db.String(100), nullable=False)
    
    # Condition types: 'extension', 'size_gt', 'size_lt', 'name_contains'
    condition_type = db.Column(db.String(50), nullable=False)
    
    # Value to match: e.g., '.jpg', '500MB', 'project'
    condition_value = db.Column(db.String(255), nullable=False)
    
    # Where to move matching files
    target_folder = db.Column(db.String(500), nullable=False)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'condition_type': self.condition_type,
            'condition_value': self.condition_value,
            'target_folder': self.target_folder,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
