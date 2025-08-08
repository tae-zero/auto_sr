"""
User Model
"""
from sqlalchemy import Column, String, Integer, Text
from app.common.database.database import Base

class UserModel(Base):
    """사용자 모델"""
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Text, nullable=False)
    industry = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    name = Column(Text, nullable=False)
    age = Column(Text, nullable=False)
    auth_id = Column(Text, nullable=False, unique=True)
    auth_pw = Column(Text, nullable=False)
