from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
# from uuid import UUID # 더 이상 필요하지 않습니다.

# Pydantic 모델을 사용하여 테이블 스키마를 클래스로 정의합니다.
class ProfileEntity(BaseModel):
    pass