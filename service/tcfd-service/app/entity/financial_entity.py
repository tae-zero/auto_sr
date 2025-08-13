"""
재무정보 엔티티
- Railway PostgreSQL 데이터베이스 테이블과 매핑
- SQLAlchemy 또는 직접 SQL 매핑
"""
from typing import Optional
from datetime import datetime
import uuid

class FinancialDataEntity:
    """재무정보 데이터베이스 엔티티"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        company_id: str = "",
        fiscal_year: str = "",
        revenue: float = 0.0,
        total_assets: float = 0.0,
        total_liabilities: float = 0.0,
        total_equity: float = 0.0,
        operating_income: Optional[float] = None,
        net_income: Optional[float] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id or str(uuid.uuid4())
        self.company_id = company_id
        self.fiscal_year = fiscal_year
        self.revenue = revenue
        self.total_assets = total_assets
        self.total_liabilities = total_liabilities
        self.total_equity = total_equity
        self.operating_income = operating_income
        self.net_income = net_income
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_id': self.company_id,
            'fiscal_year': self.fiscal_year,
            'revenue': self.revenue,
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities,
            'total_equity': self.total_equity,
            'operating_income': self.operating_income,
            'net_income': self.net_income,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FinancialDataEntity':
        """딕셔너리에서 엔티티 생성"""
        return cls(
            id=data.get('id'),
            company_id=data.get('company_id', ''),
            fiscal_year=data.get('fiscal_year', ''),
            revenue=data.get('revenue', 0.0),
            total_assets=data.get('total_assets', 0.0),
            total_liabilities=data.get('total_liabilities', 0.0),
            total_equity=data.get('total_equity', 0.0),
            operating_income=data.get('operating_income'),
            net_income=data.get('net_income'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
    
    def __repr__(self) -> str:
        return f"FinancialDataEntity(id='{self.id}', company_id='{self.company_id}', fiscal_year='{self.fiscal_year}')"
