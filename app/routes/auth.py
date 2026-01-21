from contextlib import contextmanager

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.schemas.user_schema import RegisterRequest, LoginRequest, UserResponse
from app.models.user import User
from app.utils.auth_utils import hash_password, verify_password

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@contextmanager
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@auth_bp.post("/register")
def register():
    data = RegisterRequest.model_validate(request.get_json())
    with get_db() as db:
        existing = db.query(User).filter(User.email == data.email).first()
        if existing:
            return jsonify({"error": "Email already registered"}), 400

        user = User(
            email=data.email,
            name=data.name,
            password_hash=hash_password(data.password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return (
            jsonify(UserResponse.model_validate(user).model_dump()),
            201,
        )


@auth_bp.post("/login")
def login():
    data = LoginRequest.model_validate(request.get_json())

    with get_db() as db:
        user = db.query(User).filter(User.email == data.email).first()
        if not user or not verify_password(data.password, user.password_hash):
            return jsonify({"error": "Invalid email or password"}), 401

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"email": user.email, "name": user.name},
        )

        return jsonify({"access_token": token}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())

    with get_db() as db:
        user = db.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify(UserResponse.model_validate(user).model_dump())
