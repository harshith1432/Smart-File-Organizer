from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.services.organizer import organize_files_auto, apply_custom_rules, undo_last_moves
from backend.models import OrganizationRule
from backend.extensions import db

organizer_bp = Blueprint('organizer', __name__)

@organizer_bp.route('/auto', methods=['POST'])
@jwt_required()
def auto_organize():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    source_dir = data.get('source_dir') # Optional
    
    result = organize_files_auto(user_id, source_dir)
    return jsonify(result), 200

@organizer_bp.route('/apply-rules', methods=['POST'])
@jwt_required()
def run_rules():
    user_id = get_jwt_identity()
    result = apply_custom_rules(user_id)
    return jsonify(result), 200

@organizer_bp.route('/undo', methods=['POST'])
@jwt_required()
def undo():
    user_id = get_jwt_identity()
    result = undo_last_moves(user_id)
    return jsonify(result), 200

# CRUD for custom rules

@organizer_bp.route('/rules', methods=['GET'])
@jwt_required()
def get_rules():
    user_id = get_jwt_identity()
    rules = OrganizationRule.query.filter_by(user_id=user_id).all()
    return jsonify([r.to_dict() for r in rules]), 200

@organizer_bp.route('/rules', methods=['POST'])
@jwt_required()
def create_rule():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    required = ['name', 'condition_type', 'condition_value', 'target_folder']
    for req in required:
        if not data.get(req):
            return jsonify({'error': f'Missing {req}'}), 400
            
    rule = OrganizationRule(
        user_id=user_id,
        name=data['name'],
        condition_type=data['condition_type'],
        condition_value=data['condition_value'],
        target_folder=data['target_folder'],
        is_active=data.get('is_active', True)
    )
    db.session.add(rule)
    db.session.commit()
    return jsonify(rule.to_dict()), 201

@organizer_bp.route('/rules/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_rule(rule_id):
    user_id = get_jwt_identity()
    rule = OrganizationRule.query.filter_by(id=rule_id, user_id=user_id).first()
    if not rule:
        return jsonify({'error': 'Rule not found'}), 404
        
    db.session.delete(rule)
    db.session.commit()
    return jsonify({'message': 'Rule deleted'}), 200
