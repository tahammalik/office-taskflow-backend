from sqlalchemy import Column,Integer,String,ForeignKey,DateTime,Boolean
from . import Base

class RefreshToken(Base):
    __tablename__ = 'refreshtokens'

    id = Column(Integer,primary_key=True,autoincrement=True,index=True)
    user_id = Column(Integer,unique=True,nullable=True)
    token_hash = Column(String,nullable=False)
    expires_at = Column(DateTime,nullable=False)
    created_at = Column(DateTime,nullable=False)
    is_revoked = Column(Boolean,nullable=False)
