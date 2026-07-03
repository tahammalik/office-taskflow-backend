from sqlalchemy import Column,String,Integer,DateTime,ForeignKey
from  sqlalchemy.orm import Mapped,mapped_column
from typing import Optional
from app.core.db import Base
from datetime import datetime

class TaskHistory(Base):
    __tablename__ = "taskhistory"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    changed_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    old_status: Mapped[str] = mapped_column()
    new_status: Mapped[str] = mapped_column()
    comment: Mapped[Optional[str]] = mapped_column(nullable=True)
    changed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)