from typing import List, Optional
import asyncpg
from ..entity.tcfd_draft_entity import TCFDDraftEntity

class TCFDDraftRepository:
    """TCFD 초안 데이터 Repository"""
    
    def __init__(self):
        pass
    
    async def save(self, conn: asyncpg.Connection, tcfd_draft: TCFDDraftEntity) -> TCFDDraftEntity:
        """TCFD 초안 데이터 저장"""
        query = """
        INSERT INTO tcfd_drafts (
            company_name, user_id, tcfd_input_id, draft_content, draft_type, file_path, status, created_at, updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), NOW())
        RETURNING id, company_name, user_id, tcfd_input_id, draft_content, draft_type, file_path, status, created_at, updated_at
        """
        
        result = await conn.fetchrow(
            query,
            tcfd_draft.company_name,
            tcfd_draft.user_id,
            tcfd_draft.tcfd_input_id,
            tcfd_draft.draft_content,
            tcfd_draft.draft_type,
            tcfd_draft.file_path,
            tcfd_draft.status
        )
        
        # 저장된 데이터로 Entity 생성하여 반환
        if result:
            return TCFDDraftEntity(
                id=result['id'],
                company_name=result['company_name'],
                user_id=result['user_id'],
                tcfd_input_id=result['tcfd_input_id'],
                draft_content=result['draft_content'],
                draft_type=result['draft_type'],
                file_path=result['file_path'],
                status=result['status'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        else:
            raise Exception("초안 데이터 저장 실패")
    
    async def find_by_company_name(self, conn: asyncpg.Connection, company_name: str) -> List[TCFDDraftEntity]:
        """회사명으로 초안 데이터 조회"""
        query = """
        SELECT id, company_name, user_id, tcfd_input_id, draft_content, draft_type, file_path, status, created_at, updated_at
        FROM tcfd_drafts 
        WHERE company_name = $1 
        ORDER BY created_at DESC
        """
        
        results = await conn.fetch(query, company_name)
        
        drafts = []
        for result in results:
            draft = TCFDDraftEntity(
                id=result['id'],
                company_name=result['company_name'],
                user_id=result['user_id'],
                tcfd_input_id=result['tcfd_input_id'],
                draft_content=result['draft_content'],
                draft_type=result['draft_type'],
                file_path=result['file_path'],
                status=result['status'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
            drafts.append(draft)
        
        return drafts
    
    async def find_by_id(self, conn: asyncpg.Connection, draft_id: int) -> Optional[TCFDDraftEntity]:
        """ID로 초안 데이터 조회"""
        query = """
        SELECT id, company_name, user_id, tcfd_input_id, draft_content, draft_type, file_path, status, created_at, updated_at
        FROM tcfd_drafts 
        WHERE id = $1
        """
        
        result = await conn.fetchrow(query, draft_id)
        
        if result:
            return TCFDDraftEntity(
                id=result['id'],
                company_name=result['company_name'],
                user_id=result['user_id'],
                tcfd_input_id=result['tcfd_input_id'],
                draft_content=result['draft_content'],
                draft_type=result['draft_type'],
                file_path=result['file_path'],
                status=result['status'],
                created_at=result['created_at'],
                updated_at=result['updated_at']
            )
        else:
            return None
    
    async def update_status(self, conn: asyncpg.Connection, draft_id: int, status: str) -> bool:
        """초안 데이터 상태 업데이트"""
        query = """
        UPDATE tcfd_drafts 
        SET status = $1, updated_at = NOW() 
        WHERE id = $2
        """
        
        result = await conn.execute(query, status, draft_id)
        return result == "UPDATE 1"
