"""
User Entity
"""
from pydantic import BaseModel
from typing import Optional

class UserEntity(BaseModel):
    """사용자 엔티티"""
    id: Optional[int] = None
    company_id: str
    industry: str
    email: str
    name: str
    age: str
    auth_id: str
    auth_pw: str

    class Config:
        from_attributes = True
