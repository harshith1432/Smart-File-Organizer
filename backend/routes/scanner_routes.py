from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.scanner import scan_directory
from backend.models import ScanHistory
from backend.app import db
import os
import threading

scanner_bp = Blueprint('scanner', __name__)

@scanner_bp.route('/start', methods=['POST'])
@jwt_required()
def start_scan():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    directory_path = data.get('directory_path')
    if not directory_path:
        return jsonify({"error": "Directory path is required"}), 400
    
    if not os.path.exists(directory_path) or not os.path.isdir(directory_path):
        return jsonify({"error": "Invalid directory path"}), 400

    from flask import current_app
    app = current_app._get_current_object()

    def run_scan_async(app_context, uid, path):
        with app_context.app_context():
            try:
                print(f"[SERVER] Background scan thread started for {path}")
                scan_directory(uid, path)
                print(f"[SERVER] Background scan thread finished for {path}")
            except Exception as e:
                print(f"[SERVER] Background scan thread ERROR: {e}")

    thread = threading.Thread(target=run_scan_async, args=(app, user_id, directory_path))
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Scanning started in background. Monitor the terminal/logs for progress."}), 202

@scanner_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    user_id = get_jwt_identity()
    history = ScanHistory.query.filter_by(user_id=user_id).order_by(ScanHistory.start_time.desc()).limit(10).all()
    return jsonify([h.to_dict() for h in history]), 200
