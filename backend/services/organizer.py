import os
import shutil
from datetime import datetime
from backend.models import FileRecord, ActivityLog, OrganizationRule
from backend.extensions import db
import json

def organize_files_auto(user_id, source_dir=None):
    """
    Auto-organize files based on their category.
    If source_dir is provided, only files in that dir are organized.
    Otherwise, all known files for user are organized.
    """
    query = FileRecord.query.filter_by(user_id=user_id)
    if source_dir:
        # Simple prefix match for demonstration
        query = query.filter(FileRecord.current_path.startswith(source_dir))
    
    files = query.all()
    moved_count = 0
    errors = []

    for f in files:
        if f.category == 'Others' or f.category == 'Uncategorized':
            continue # Don't auto-move uncategorized things blindly
            
        # Target dir: Base Directory of the file / Category Name
        # E.g., C:/Downloads/Images/file.jpg
        base_dir = os.path.dirname(f.current_path)
        
        # Prevent moving if it's already in a folder named like its category
        if os.path.basename(base_dir) == f.category:
            continue
            
        target_dir = os.path.join(base_dir, f.category)
        target_path = os.path.join(target_dir, f.filename)
        
        moved = move_file(f, target_path, target_dir)
        if moved:
            moved_count += 1
        else:
            errors.append(f"Failed to move {f.filename}")

    # Log action
    if moved_count > 0:
        log = ActivityLog(
            user_id=user_id,
            action='auto_organized',
            details=f"Auto-organized {moved_count} files."
        )
        db.session.add(log)
        db.session.commit()
        
    return {"moved_count": moved_count, "errors": errors}


def apply_custom_rules(user_id):
    rules = OrganizationRule.query.filter_by(user_id=user_id, is_active=True).all()
    files = FileRecord.query.filter_by(user_id=user_id).all()
    
    moved_count = 0
    
    for rule in rules:
        for f in files:
            # Check condition
            match = False
            if rule.condition_type == 'extension':
                if f.extension and f.extension.lower() == rule.condition_value.lower():
                    match = True
            elif rule.condition_type == 'size_gt':
                try:
                    # simplistic parse (assuming bytes for now. In real app, standardise units)
                    if f.size > int(rule.condition_value):
                        match = True
                except: pass
            elif rule.condition_type == 'name_contains':
                if rule.condition_value.lower() in f.filename.lower():
                    match = True
                    
            if match:
                target_path = os.path.join(rule.target_folder, f.filename)
                # prevent moving to same place
                if f.current_path != target_path:
                    if move_file(f, target_path, rule.target_folder):
                        moved_count += 1
                        
    if moved_count > 0:
        log = ActivityLog(
            user_id=user_id,
            action='custom_rules_applied',
            details=f"Moved {moved_count} files via custom rules."
        )
        db.session.add(log)
        db.session.commit()
        
    return {"moved_count": moved_count}


def move_file(file_record, target_path, target_dir):
    try:
        # Create dir if not exists
        os.makedirs(target_dir, exist_ok=True)
        
        # Handle filename collisions
        base, extension = os.path.splitext(file_record.filename)
        counter = 1
        final_target_path = target_path
        
        while os.path.exists(final_target_path):
            if final_target_path == file_record.current_path:
                return False # Already exists at exact same path
            new_name = f"{base}_{counter}{extension}"
            final_target_path = os.path.join(target_dir, new_name)
            counter += 1
            
        shutil.move(file_record.current_path, final_target_path)
        
        # Update record
        file_record.current_path = final_target_path
        # We assume original filename shouldn't change in DB, just the path, but let's update filename if we altered it
        file_record.filename = os.path.basename(final_target_path)
        db.session.commit()
        return True
    except Exception as e:
        print(f"Error moving {file_record.current_path}: {e}")
        return False


def undo_last_moves(user_id):
    """
    Simplified undo: move files back to their original_path.
    In a full app, you might want to track 'last_move_source' specifically.
    """
    files = FileRecord.query.filter_by(user_id=user_id).all()
    restored = 0
    errors = []
    
    for f in files:
        if f.current_path != f.original_path:
            target_dir = os.path.dirname(f.original_path)
            moved = move_file(f, f.original_path, target_dir)
            if moved:
                f.current_path = f.original_path
                db.session.commit()
                restored += 1
            else:
                errors.append(f"Failed restoring {f.filename}")
                
    if restored > 0:
        log = ActivityLog(
            user_id=user_id,
            action='undo_operations',
            details=f"Restored {restored} files to original locations."
        )
        db.session.add(log)
        db.session.commit()
        
    return {"restored_count": restored, "errors": errors}
