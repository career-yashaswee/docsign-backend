import os
import uuid
from werkzeug.utils import secure_filename
from typing import Iterable
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.document import Document


def allowed_file(filename: str, allowed_exts: Iterable[str]) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in set(x.lower() for x in allowed_exts)


def save_uploaded_file(file_storage, user_id: int) -> str:
    """
    Saves the file under UPLOAD_DIR/<user_id>/<uuid>.<ext>
    Returns the relative path (to store in DB).
    """
    filename = secure_filename(file_storage.filename or "")
    if not filename:
        raise ValueError("Invalid filename")
    if not allowed_file(filename, settings.ALLOWED_EXTENSIONS):
        raise ValueError("File type not allowed")

    ext = filename.rsplit(".", 1)[1].lower()
    uid = uuid.uuid4().hex
    user_dir = os.path.join(settings.UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)

    stored_name = f"{uid}.{ext}"
    full_path = os.path.join(user_dir, stored_name)
    file_storage.save(full_path)

    # Return path relative to project root (or absolute; your choice)
    return full_path


def create_document(db: Session, owner_id: int, title: str, file_path: str) -> Document:
    doc = Document(
        owner_id=owner_id,
        title=title,
        file_path=file_path,
        status="pending",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc
