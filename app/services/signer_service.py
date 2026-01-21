from typing import List, Dict, Set
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.models.document import Document
from app.models.signer import DocumentSigner


class AssignSignersError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status
        super().__init__(message)


def assign_signers(
    db: Session, *, doc_id: int, requester_id: int, signer_ids: List[int]
) -> Dict[str, List[int]]:
    """
    Assigns signers to a document; only the owner can assign.
    Returns a dict that classifies each input user id.
    """
    # Load document and authorize
    doc = db.get(Document, doc_id)
    if not doc:
        raise AssignSignersError("not_found", "Document not found", status=404)
    if doc.owner_id != requester_id:
        raise AssignSignersError(
            "forbidden", "Only owner can assign signers", status=403
        )

    # Deduplicate inputs, and remove obvious junk
    input_ids: List[int] = [
        int(x) for x in signer_ids if isinstance(x, int) or str(x).isdigit()
    ]
    unique_ids: List[int] = list(dict.fromkeys(input_ids))  # preserve order but dedupe

    # Reject self-assignment
    self_rejected = [uid for uid in unique_ids if uid == requester_id]
    candidate_ids: List[int] = [uid for uid in unique_ids if uid != requester_id]
    if not candidate_ids and not self_rejected:
        return {
            "assigned": [],
            "already_assigned": [],
            "invalid_user_ids": [],
            "self_assignment_rejected": [],
        }

    # Validate users exist
    if candidate_ids:
        rows = (
            db.execute(select(User.id).where(User.id.in_(candidate_ids)))
            .scalars()
            .all()
        )
        existing: Set[int] = set(rows)
    else:
        existing = set()

    invalid = [uid for uid in candidate_ids if uid not in existing]
    valid_candidates = [uid for uid in candidate_ids if uid in existing]

    if not valid_candidates and not self_rejected:
        # nothing to do, only invalids
        return {
            "assigned": [],
            "already_assigned": [],
            "invalid_user_ids": invalid,
            "self_assignment_rejected": [],
        }

    # Find already assigned
    if valid_candidates:
        rows = (
            db.execute(
                select(DocumentSigner.signer_id).where(
                    (DocumentSigner.document_id == doc_id)
                    & (DocumentSigner.signer_id.in_(valid_candidates))
                )
            )
            .scalars()
            .all()
        )
        already_assigned = set(rows)
    else:
        already_assigned = set()

    to_insert = [uid for uid in valid_candidates if uid not in already_assigned]

    assigned: List[int] = []
    # Transactionally insert
    if to_insert:
        for uid in to_insert:
            db.add(DocumentSigner(document_id=doc_id, signer_id=uid, status="pending"))
        db.commit()

        # Re-query what got inserted (or trust to_insert)
        assigned = to_insert

    return {
        "assigned": assigned,
        "already_assigned": list(already_assigned),
        "invalid_user_ids": invalid,
        "self_assignment_rejected": self_rejected,
    }
