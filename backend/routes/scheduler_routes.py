from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import ScheduledTask
from backend.extensions import db, scheduler
from backend.services.scanner import scan_directory
from backend.services.organizer import organize_files_auto

scheduler_bp = Blueprint('scheduler', __name__)

def background_scan_task(app, user_id, path):
    with app.app_context():
        print(f"Running scheduled scan for user {user_id} on {path}")
        scan_directory(user_id, path)

def background_organize_task(app, user_id):
    with app.app_context():
        print(f"Running scheduled organization for user {user_id}")
        organize_files_auto(user_id)


@scheduler_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    tasks = ScheduledTask.query.filter_by(user_id=user_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200

@scheduler_bp.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    from flask import current_app
    user_id = get_jwt_identity()
    data = request.get_json()
    
    task_type = data.get('task_type') # 'scan' or 'organize'
    schedule = data.get('schedule') # 'daily', 'weekly'
    path = data.get('path', None) # needed if scan
    
    if not task_type or not schedule:
        return jsonify({'error': 'Missing type or schedule'}), 400
        
    task = ScheduledTask(
        user_id=user_id,
        task_type=task_type,
        schedule=schedule,
        is_active=True
    )
    db.session.add(task)
    db.session.commit()
    
    # Register with APScheduler
    job_id = f"task_{task.id}"
    app = current_app._get_current_object()
    
    if task_type == 'scan' and path:
        if schedule == 'daily':
            scheduler.add_job(id=job_id, func=background_scan_task, args=[app, user_id, path], trigger='interval', days=1)
        elif schedule == 'weekly':
            scheduler.add_job(id=job_id, func=background_scan_task, args=[app, user_id, path], trigger='interval', weeks=1)
    elif task_type == 'organize':
        if schedule == 'daily':
            scheduler.add_job(id=job_id, func=background_organize_task, args=[app, user_id], trigger='interval', days=1)
            
    return jsonify(task.to_dict()), 201

@scheduler_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = ScheduledTask.query.filter_by(id=task_id, user_id=user_id).first()
    if not task:
        return jsonify({'error': 'Task not found'}), 404
        
    db.session.delete(task)
    db.session.commit()
    
    job_id = f"task_{task_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        
    return jsonify({'message': 'Task deleted'}), 200
