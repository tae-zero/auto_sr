from datetime import datetime
from typing import Optional

class TCFDInputEntity:
    """TCFD 입력 데이터 Entity"""
    
    def __init__(
        self,
        company_name: str,
        user_id: Optional[str] = None,
        governance_g1: Optional[str] = None,
        governance_g2: Optional[str] = None,
        strategy_s1: Optional[str] = None,
        strategy_s2: Optional[str] = None,
        strategy_s3: Optional[str] = None,
        risk_management_r1: Optional[str] = None,
        risk_management_r2: Optional[str] = None,
        risk_management_r3: Optional[str] = None,
        metrics_targets_m1: Optional[str] = None,
        metrics_targets_m2: Optional[str] = None,
        metrics_targets_m3: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.company_name = company_name
        self.user_id = user_id
        self.governance_g1 = governance_g1
        self.governance_g2 = governance_g2
        self.strategy_s1 = strategy_s1
        self.strategy_s2 = strategy_s2
        self.strategy_s3 = strategy_s3
        self.risk_management_r1 = risk_management_r1
        self.risk_management_r2 = risk_management_r2
        self.risk_management_r3 = risk_management_r3
        self.metrics_targets_m1 = metrics_targets_m1
        self.metrics_targets_m2 = metrics_targets_m2
        self.metrics_targets_m3 = metrics_targets_m3
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> dict:
        """Entity를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'user_id': self.user_id,
            'governance_g1': self.governance_g1,
            'governance_g2': self.governance_g2,
            'strategy_s1': self.strategy_s1,
            'strategy_s2': self.strategy_s2,
            'strategy_s3': self.strategy_s3,
            'risk_management_r1': self.risk_management_r1,
            'risk_management_r2': self.risk_management_r2,
            'risk_management_r3': self.risk_management_r3,
            'metrics_targets_m1': self.metrics_targets_m1,
            'metrics_targets_m2': self.metrics_targets_m2,
            'metrics_targets_m3': self.metrics_targets_m3,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TCFDInputEntity':
        """딕셔너리에서 Entity 생성"""
        return cls(
            id=data.get('id'),
            company_name=data['company_name'],
            user_id=data.get('user_id'),
            governance_g1=data.get('governance_g1'),
            governance_g2=data.get('governance_g2'),
            strategy_s1=data.get('strategy_s1'),
            strategy_s2=data.get('strategy_s2'),
            strategy_s3=data.get('strategy_s3'),
            risk_management_r1=data.get('risk_management_r1'),
            risk_management_r2=data.get('risk_management_r2'),
            risk_management_r3=data.get('risk_management_r3'),
            metrics_targets_m1=data.get('metrics_targets_m1'),
            metrics_targets_m2=data.get('metrics_targets_m2'),
            metrics_targets_m3=data.get('metrics_targets_m3'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
