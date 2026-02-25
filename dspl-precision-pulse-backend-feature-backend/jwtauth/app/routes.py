from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from .extensions import db
from .models import User
from .auth import role_required

api = Blueprint("api", __name__)

@api.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Email already exists"}), 400

    user = User(
        username=data["username"],
        email=data["email"],
        role=data.get("role", "user")
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created"}), 201

@api.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(
        identity=user.id,
        additional_claims={"role": user.role}
    )

    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    })


@api.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access = create_access_token(identity=identity)
    return jsonify({"access_token": new_access})


@api.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    })


@api.route("/admin/users", methods=["GET"])
@role_required("admin")
def all_users():
    users = User.query.all()
    return jsonify([
        {"id": u.id, "email": u.email, "role": u.role}
        for u in users
    ])
