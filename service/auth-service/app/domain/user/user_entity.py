from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, func, text
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserEntity(Base):
  pass