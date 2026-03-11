from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import FileRecord, Duplicate, ActivityLog
from backend.extensions import db
import os

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard_stats():
    user_id = get_jwt_identity()
    
    # 1. Total files scanned & Organized files (any file not in 'Uncategorized'/'Others' that has current_path != original_path maybe, 
    # but let's just use total known files for "scanned" and categorized files for "organized")
    total_files = FileRecord.query.filter_by(user_id=user_id).count()
    organized_files = FileRecord.query.filter(
        FileRecord.user_id == user_id, 
        FileRecord.category.notin_(['Others', 'Uncategorized'])
    ).count()
    
    # 2. Duplicate detection stats
    duplicates = Duplicate.query.filter_by(user_id=user_id).all()
    dup_count = len(duplicates)
    wasted_space = sum(d.total_wasted_space for d in duplicates)
    
    # 3. Category distribution
    from sqlalchemy import func
    category_counts = db.session.query(
        FileRecord.category, func.count(FileRecord.id)
    ).filter_by(user_id=user_id).group_by(FileRecord.category).all()
    
    cat_distribution = {cat: count for cat, count in category_counts}
    
    # 4. Total Storage Usage known to system
    total_size = db.session.query(func.sum(FileRecord.size)).filter_by(user_id=user_id).scalar() or 0

    return jsonify({
        'total_files': total_files,
        'organized_files': organized_files,
        'duplicate_groups': dup_count,
        'wasted_space_bytes': wasted_space,
        'category_distribution': cat_distribution,
        'total_storage_bytes': total_size
    }), 200


@analytics_bp.route('/duplicates', methods=['GET'])
@jwt_required()
def get_duplicates():
    user_id = get_jwt_identity()
    duplicates = Duplicate.query.filter_by(user_id=user_id).all()
    # Filter out resolved duplicates (where files might have been deleted)
    # Ideally, a cleanup task ensures DB reflects FS. We will just return DB state.
    valid_dups = [d.to_dict() for d in duplicates if len(d.to_dict()['file_paths']) > 1]
    return jsonify(valid_dups), 200


@analytics_bp.route('/duplicates/resolve', methods=['POST'])
@jwt_required()
def resolve_duplicate():
    """ Delete specific files from a duplicate group to resolve it """
    from flask import request
    user_id = get_jwt_identity()
    data = request.get_json()
    duplicate_id = data.get('duplicate_id')
    paths_to_delete = data.get('paths_to_delete', [])
    
    dup = Duplicate.query.filter_by(id=duplicate_id, user_id=user_id).first()
    if not dup:
        return jsonify({'error': 'Duplicate group not found'}), 404
        
    deleted_count = 0
    import json
    current_paths = json.loads(dup.file_paths)
    
    for path in paths_to_delete:
        if path in current_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                current_paths.remove(path)
                deleted_count += 1
                
                # Update FileRecord
                fr = FileRecord.query.filter_by(user_id=user_id, current_path=path).first()
                if fr:
                    db.session.delete(fr)
            except Exception as e:
                print(f"Error deleting duplicate {path}: {e}")
                
    if deleted_count > 0:
        dup.file_paths = json.dumps(current_paths)
        if len(current_paths) <= 1:
            db.session.delete(dup) # Resolved
            
        log = ActivityLog(
            user_id=user_id,
            action='duplicates_resolved',
            details=f"Deleted {deleted_count} duplicate files."
        )
        db.session.add(log)
        db.session.commit()
        
    return jsonify({'message': f'Deleted {deleted_count} files.'}), 200

@analytics_bp.route('/large-files', methods=['GET'])
@jwt_required()
def get_large_files():
    from flask import request
    user_id = get_jwt_identity()
    size_threshold = int(request.args.get('min_size_mb', 100)) * 1024 * 1024 # default 100MB
    
    large_files = FileRecord.query.filter(
        FileRecord.user_id == user_id,
        FileRecord.size >= size_threshold
    ).order_by(FileRecord.size.desc()).limit(50).all()
    
    return jsonify([f.to_dict() for f in large_files]), 200

@analytics_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    user_id = get_jwt_identity()
    logs = ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.timestamp.desc()).limit(50).all()
    return jsonify([l.to_dict() for l in logs]), 200
