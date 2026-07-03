from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.core.db import Base

"""class TeamAccess:
    def __init__(self,team_id,team_name,description):
        self.team_id = team_id
        self.team_name = team_name
        self.description = description"""

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), default=None)
    team_id = Column(Integer,default=None)

    # Relationships
    workspace = relationship("Workspace", foreign_keys=[workspace_id], back_populates="users")
    created_tasks = relationship("Task", foreign_keys="Task.created_by", back_populates="creator_manager")
    assigned_tasks = relationship("Task", foreign_keys="Task.assign_to", back_populates="assigned_employee")
    led_teams = relationship("Team", back_populates="leader")
    sent_invitations = relationship("Invitation",foreign_keys="Invitation.invited_by",back_populates="inviter",)
    teams = relationship("Team", secondary="team_members", back_populates="members")