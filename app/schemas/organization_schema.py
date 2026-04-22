from pydantic import BaseModel, ConfigDict,Field
from typing import Optional
from datetime import datetime

class CreateOrganization(BaseModel):
    name: str = Field(min_length=4,max_length=100)


class ResponseOrganization(BaseModel):
    id: int
    name: str
    created_at: datetime
    created_by: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)     # helps pydantic to work with sqlalchemy

class UpdateOrganization(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    is_active: Optional[bool]
