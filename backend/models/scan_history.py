from datetime import datetime
from backend.extensions import db

class ScanHistory(db.Model):
    __tablename__ = 'scan_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    path_scanned = db.Column(db.String(1024), nullable=False)
    files_found = db.Column(db.Integer, default=0)
    total_size = db.Column(db.BigInteger, default=0) # Total bytes scanned
    
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='in_progress') # in_progress, completed, failed
    
    def to_dict(self):
        return {
            'id': self.id,
            'path_scanned': self.path_scanned,
            'files_found': self.files_found,
            'total_size': self.total_size,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'status': self.status
        }
