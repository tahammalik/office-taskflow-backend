from datetime import datetime, timedelta, timezone
import secrets
from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"), nullable=False)
    invited_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String, default="user", nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)  # pending/accepted/expired/revoked
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    workspace = relationship("Workspace", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by])

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def default_expiry(days: int = 7) -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=days)