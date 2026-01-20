from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, func
from sqlalchemy.orm import relationship
from app.core.db import Base


class DocumentSigner(Base):
    __tablename__ = "document_signers"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    signer_id = Column(Integer, ForeignKey("users.id"))

    status = Column(String, default="pending")  # pending | signed | rejected
    signed_at = Column(DateTime(timezone=True))

    document = relationship("Document", back_populates="signers")
    signer = relationship("User")
