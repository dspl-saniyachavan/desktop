from flask import Blueprint, request, jsonify
from app.controllers.parameter_controller import ParameterController
from app.middleware.auth_middleware import token_required

parameter_bp = Blueprint('parameters', __name__, url_prefix='/api/parameters')

@parameter_bp.route('', methods=['GET'])
@token_required
def get_parameters():
    """Get all parameters"""
    result, status = ParameterController.get_all_parameters()
    return jsonify(result), status

@parameter_bp.route('', methods=['POST'])
@token_required
def create_parameter():
    """Create a new parameter"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result, status = ParameterController.create_parameter(data)
    return jsonify(result), status

@parameter_bp.route('/<int:param_id>', methods=['GET'])
@token_required
def get_parameter(param_id):
    """Get a specific parameter by ID"""
    result, status = ParameterController.get_parameter_by_id(param_id)
    return jsonify(result), status

@parameter_bp.route('/<int:param_id>', methods=['PUT'])
@token_required
def update_parameter(param_id):
    """Update a parameter"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result, status = ParameterController.update_parameter(param_id, data)
    return jsonify(result), status

@parameter_bp.route('/<int:param_id>', methods=['DELETE'])
@token_required
def delete_parameter(param_id):
    """Delete a parameter"""
    result, status = ParameterController.delete_parameter(param_id)
    return jsonify(result), status
