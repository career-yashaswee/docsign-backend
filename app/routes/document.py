from contextlib import contextmanager

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.document import Document
from app.models.signer import DocumentSigner
from app.models.comment import DocumentComment
from app.schemas.document_schema import (
    CreateDocumentForm,
    DocumentOut,
    DocumentDetailOut,
)
from app.services.document_service import save_uploaded_file, create_document
from app.utils.pagination import get_pagination_params, build_paginated_response

documents_bp = Blueprint("documents", __name__, url_prefix="/api/v1/documents")


@contextmanager
def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@documents_bp.post("")
@jwt_required()
def upload_document():
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return jsonify({"error": "file is required"}), 400

    file = request.files["file"]
    title_value = request.form.get("title", "").strip()

    try:
        form = CreateDocumentForm(title=title_value)
    except Exception as e:
        return jsonify({"error": "validation_error", "detail": str(e)}), 422

    if file.filename == "":
        return jsonify({"error": "empty filename"}), 400

    try:
        file_path = save_uploaded_file(file, user_id)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    with get_db() as db:
        doc = create_document(
            db, owner_id=user_id, title=form.title, file_path=file_path
        )
        return jsonify(DocumentOut.model_validate(doc).model_dump()), 201


@documents_bp.get("")
@jwt_required()
def list_documents():
    user_id = int(get_jwt_identity())
    page, page_size, offset = get_pagination_params()

    with get_db() as db:
        q = (
            db.query(Document)
            .outerjoin(DocumentSigner, DocumentSigner.document_id == Document.id)
            .filter(
                (Document.owner_id == user_id) | (DocumentSigner.signer_id == user_id)
            )
            .order_by(Document.created_at.desc())
            .distinct()
        )

        total = q.count()
        rows = q.limit(page_size).offset(offset).all()

        data = [DocumentOut.model_validate(r).model_dump() for r in rows]
        return jsonify(build_paginated_response(data, total, page, page_size)), 200


@documents_bp.get("/<int:doc_id>")
@jwt_required()
def get_document(doc_id: int):
    user_id = int(get_jwt_identity())

    with get_db() as db:
        doc = (
            db.query(Document)
            .outerjoin(DocumentSigner, DocumentSigner.document_id == Document.id)
            .filter(Document.id == doc_id)
            .filter(
                (Document.owner_id == user_id) | (DocumentSigner.signer_id == user_id)
            )
            .first()
        )
        if not doc:
            return jsonify({"error": "not_found"}), 404

        signers_count = (
            db.query(func.count(DocumentSigner.id))
            .filter(DocumentSigner.document_id == doc.id)
            .scalar()
        ) or 0
        comments_count = (
            db.query(func.count(DocumentComment.id))
            .filter(DocumentComment.document_id == doc.id)
            .scalar()
        ) or 0

        payload = DocumentDetailOut(
            id=doc.id,
            owner_id=doc.owner_id,
            title=doc.title,
            file_path=doc.file_path,
            status=doc.status,
            created_at=doc.created_at,
            signers_count=signers_count,
            comments_count=comments_count,
        ).model_dump()

        return jsonify(payload), 200
