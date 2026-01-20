from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.db import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # path to file (local or GCS)
    status = Column(String, default="pending")  # pending | partially_signed | signed

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User")
    signers = relationship("DocumentSigner", back_populates="document")
    comments = relationship("DocumentComment", back_populates="document")
