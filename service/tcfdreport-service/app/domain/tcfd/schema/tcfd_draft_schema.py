from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TCFDDraftCreateSchema(BaseModel):
    """TCFD 초안 데이터 생성 스키마"""
    
    company_name: str = Field(..., description="회사명", min_length=1, max_length=255)
    user_id: Optional[str] = Field(None, description="사용자 ID", max_length=255)
    tcfd_input_id: Optional[int] = Field(None, description="TCFD 입력 데이터 ID")
    draft_content: Optional[str] = Field(None, description="초안 내용")
    draft_type: Optional[str] = Field(None, description="초안 타입 (pdf, word, html 등)")
    file_path: Optional[str] = Field(None, description="파일 경로")
    status: str = Field(default="processing", description="상태")

class TCFDDraftUpdateSchema(BaseModel):
    """TCFD 초안 데이터 업데이트 스키마"""
    
    draft_content: Optional[str] = Field(None, description="초안 내용")
    draft_type: Optional[str] = Field(None, description="초안 타입")
    file_path: Optional[str] = Field(None, description="파일 경로")
    status: Optional[str] = Field(None, description="상태")

class TCFDDraftResponseSchema(BaseModel):
    """TCFD 초안 데이터 응답 스키마"""
    
    id: int = Field(..., description="초안 데이터 ID")
    company_name: str = Field(..., description="회사명")
    user_id: Optional[str] = Field(None, description="사용자 ID")
    tcfd_input_id: Optional[int] = Field(None, description="TCFD 입력 데이터 ID")
    draft_content: Optional[str] = Field(None, description="초안 내용")
    draft_type: Optional[str] = Field(None, description="초안 타입")
    file_path: Optional[str] = Field(None, description="파일 경로")
    status: str = Field(..., description="상태")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")
    
    class Config:
        from_attributes = True
