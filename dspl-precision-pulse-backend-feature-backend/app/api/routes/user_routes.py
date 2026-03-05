from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from services.user_service import UserService

user_bp = Blueprint("users", __name__)

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    user = UserService.register_user(
        data["username"],
        data["password"],
        data["role"]
    )
    return jsonify({"id": user.id}), 201


@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = UserService.authenticate(
        data["username"],
        data["password"]
    )

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"access_token": token})
