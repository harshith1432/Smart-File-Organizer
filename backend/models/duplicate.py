from datetime import datetime
from backend.extensions import db

class Duplicate(db.Model):
    __tablename__ = 'duplicates'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    hash_value = db.Column(db.String(64), nullable=False)
    
    # Stored as JSON string or a list of paths
    file_paths = db.Column(db.Text, nullable=False) 
    total_wasted_space = db.Column(db.BigInteger, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'hash_value': self.hash_value,
            'file_paths': json.loads(self.file_paths),
            'total_wasted_space': self.total_wasted_space,
            'created_at': self.created_at.isoformat()
        }
