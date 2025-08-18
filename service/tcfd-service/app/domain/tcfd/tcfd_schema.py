from pydantic import BaseModel
from typing import List, Optional

class TCFDStandardResponse(BaseModel):
    id: int
    category: str
    disclosure_id: str
    disclosure_summary: str
    disclosure_detail: str

    class Config:
        from_attributes = True

class TCFDStandardsListResponse(BaseModel):
    success: bool
    message: str
    data: List[TCFDStandardResponse]
