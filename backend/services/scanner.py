import os
import hashlib
from datetime import datetime
from backend.models import FileRecord, ScanHistory, ActivityLog, Duplicate
from backend.extensions import db
import time

CATEGORIES = {
    'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.csv', '.ppt', '.pptx'],
    'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
    'Videos': ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm'],
    'Audio': ['.mp3', '.wav', '.aac', '.ogg', '.flac', '.m4a'],
    'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Code Files': ['.py', '.js', '.html', '.css', '.java', '.c', '.cpp', '.php', '.sql', '.json', '.xml', '.jsx', '.ts', '.tsx', '.md'],
    'Executables': ['.exe', '.msi', '.apk', '.dmg', '.sh', '.bat']
}

def get_category(extension):
    ext_lower = extension.lower()
    for category, exts in CATEGORIES.items():
        if ext_lower in exts:
            return category
    return 'Others'

def calculate_hash(filepath, chunk_size=8192):
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"Error hashing {filepath}: {e}")
        return None

def scan_directory(user_id, directory_path):
    """
    Scans a directory recursively, extracts metadata, 
    and saves FileRecords to the database.
    Also records ScanHistory.
    """
    print(f"\n[SCANNER] Starting scan of: {directory_path}")
    scan_history = ScanHistory(
        user_id=user_id,
        path_scanned=directory_path,
        start_time=datetime.utcnow(),
        status='in_progress'
    )
    db.session.add(scan_history)
    db.session.commit()

    total_files = 0
    total_size = 0
    processed_count = 0
    
    # We will compute hashes for duplicate detection
    hash_dict = {} # hash -> [list of paths]

    try:
        for root, _, files in os.walk(directory_path):
            for file in files:
                filepath = os.path.join(root, file)
                
                try:
                    # Skip symlinks and inaccessible files
                    if os.path.islink(filepath) or not os.access(filepath, os.R_OK):
                        continue
                        
                    stat = os.stat(filepath)
                    size = stat.st_size
                    total_size += size
                    total_files += 1
                    
                    _, ext = os.path.splitext(file)
                    category = get_category(ext)
                    
                    print(f"[SCANNER] Processing ({total_files}): {file}")
                    
                    # Basic metadata
                    file_record = FileRecord.query.filter_by(
                        user_id=user_id, 
                        original_path=filepath
                    ).first()
                    
                    if not file_record:
                        file_record = FileRecord(
                            user_id=user_id,
                            original_path=filepath,
                            current_path=filepath,
                            filename=file,
                            extension=ext,
                            size=size,
                            category=category,
                            file_hash=calculate_hash(filepath)
                        )
                        db.session.add(file_record)
                    else:
                        # Update existing
                        file_record.size = size
                        if not file_record.file_hash:
                            file_record.file_hash = calculate_hash(filepath)

                    # Track hashes for duplicates
                    if file_record.file_hash:
                        h = file_record.file_hash
                        if h not in hash_dict:
                            hash_dict[h] = []
                        hash_dict[h].append(filepath)
                    
                    processed_count += 1
                    # Batch commit every 50 files to show progress and save state
                    if processed_count % 50 == 0:
                        db.session.commit()
                        print(f"[SCANNER] Progress: {total_files} files scanned so far...")

                except Exception as e:
                    print(f"[SCANNER] Error processing file {filepath}: {e}")

        # Update Scan History
        scan_history.files_found = total_files
        scan_history.total_size = total_size
        scan_history.end_time = datetime.utcnow()
        scan_history.status = 'completed'
        
        # Log Activity
        log = ActivityLog(
            user_id=user_id,
            action='scanned_directory',
            details=f"Scanned {directory_path}. Found {total_files} files."
        )
        db.session.add(log)
        db.session.commit()
        
        print(f"[SCANNER] Completed! Total files found: {total_files}")
        
        # Process duplicates found during this scan
        print("[SCANNER] Analyzing duplicates...")
        process_duplicates(user_id, hash_dict)

        return {
            "message": "Scan completed successfully",
            "files_found": total_files,
            "total_size": total_size
        }

    except Exception as e:
        print(f"[SCANNER] FATAL ERROR: {str(e)}")
        scan_history.status = 'failed'
        db.session.commit()
        return {"error": str(e)}

def process_duplicates(user_id, hash_dict):
    import json
    for hash_val, paths in hash_dict.items():
        if len(paths) > 1:
            # We found duplicates
            existing_dup = Duplicate.query.filter_by(user_id=user_id, hash_value=hash_val).first()
            
            # Calculate wasted space (size of one file * (number of copies - 1))
            try:
                sample_size = os.path.getsize(paths[0])
                wasted = sample_size * (len(paths) - 1)
            except:
                wasted = 0

            if existing_dup:
                # Update existing duplicate record
                # Merge existing paths with new paths, removing actual exact duplicates in the list
                existing_paths = json.loads(existing_dup.file_paths)
                all_paths = list(set(existing_paths + paths))
                existing_dup.file_paths = json.dumps(all_paths)
                
                # Recalculate wasted
                if wasted > 0:
                    try:
                        sz = os.path.getsize(all_paths[0])
                        existing_dup.total_wasted_space = sz * (len(all_paths) - 1)
                    except:
                        pass
            else:
                new_dup = Duplicate(
                    user_id=user_id,
                    hash_value=hash_val,
                    file_paths=json.dumps(list(set(paths))),
                    total_wasted_space=wasted
                )
                db.session.add(new_dup)
    db.session.commit()
