from contextlib import contextmanager
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.schemas.signer_schema import AssignSignersRequest, AssignSignersResult
from app.services.signer_service import assign_signers, AssignSignersError

signers_bp = Blueprint("signers", __name__, url_prefix="/api/v1/documents")


@contextmanager
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@signers_bp.post("/<int:doc_id>/assign-signers")
@jwt_required()
def assign_document_signers(doc_id: int):
    user_id = int(get_jwt_identity())

    try:
        body = AssignSignersRequest.model_validate(request.get_json() or {})
    except Exception as e:
        return jsonify({"error": "validation_error", "detail": str(e)}), 422

    with get_db() as db:
        try:
            result = assign_signers(
                db,
                doc_id=doc_id,
                requester_id=user_id,
                signer_ids=body.signers,
            )
        except AssignSignersError as ae:
            return jsonify({"error": ae.code, "message": ae.message}), ae.status

        return jsonify(AssignSignersResult(**result).model_dump()), 200
