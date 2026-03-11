from datetime import datetime
from backend.extensions import db

class FileRecord(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # File details
    original_path = db.Column(db.String(1024), nullable=False)
    current_path = db.Column(db.String(1024), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    extension = db.Column(db.String(50))
    size = db.Column(db.BigInteger, nullable=False) # Size in bytes
    file_hash = db.Column(db.String(64)) # SHA-256
    
    # Organization metadata
    category = db.Column(db.String(100), default='Uncategorized')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # When added to DB
    modified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'original_path': self.original_path,
            'current_path': self.current_path,
            'filename': self.filename,
            'extension': self.extension,
            'size': self.size,
            'file_hash': self.file_hash,
            'category': self.category,
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None
        }
