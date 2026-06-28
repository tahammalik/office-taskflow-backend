from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base

class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True,autoincrement=True, index=True)
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)
    token = Column(String, unique=True, nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    invited_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")
    expires_at = Column(String, nullable=False)

    workspace = relationship("Workspace", back_populates="invitations")
    inviter = relationship("User", back_populates="sent_invitations")