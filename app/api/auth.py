import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

@auth_bp.post("/register")
def register():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    # First registered user can be admin, or you can pass "is_admin": true in payload
    is_admin = data.get("is_admin", False) 
    
    user = User(email=email, is_admin=is_admin)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()

    # Generate tokens
    access_token = create_access_token(
        identity=str(user.id), 
        additional_claims={"is_admin": user.is_admin}
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 201


@auth_bp.post("/login")
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"].strip().lower()
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    access_token = create_access_token(
        identity=str(user.id), 
        additional_claims={"is_admin": user.is_admin}
    )
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "user": user.to_dict(),
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    access_token = create_access_token(
        identity=str(user.id), 
        additional_claims={"is_admin": user.is_admin}
    )
    return jsonify({"access_token": access_token}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    identity = get_jwt_identity()
    user = User.query.get(int(identity))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user": user.to_dict()}), 200