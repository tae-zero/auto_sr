"""
TCFD Service TCFD 엔티티
- TCFD 데이터베이스 엔티티
- AI 분석 결과, 위험 평가, 보고서 생성
"""
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

class TCFDEntity:
    """TCFD 분석 및 보고서 엔티티"""
    
    def __init__(
        self,
        entity_id: Optional[str] = None,
        company_info: Optional[Dict[str, Any]] = None,
        financial_data: Optional[Dict[str, Any]] = None,
        risk_assessment: Optional[Dict[str, Any]] = None,
        analysis_result: Optional[Dict[str, Any]] = None,
        report_result: Optional[Dict[str, Any]] = None,
        status: str = "pending",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.entity_id = entity_id or str(uuid.uuid4())
        self.company_info = company_info or {}
        self.financial_data = financial_data or {}
        self.risk_assessment = risk_assessment or {}
        self.analysis_result = analysis_result or {}
        self.report_result = report_result or {}
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            'entity_id': self.entity_id,
            'company_info': self.company_info,
            'financial_data': self.financial_data,
            'risk_assessment': self.risk_assessment,
            'analysis_result': self.analysis_result,
            'report_result': self.report_result,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TCFDEntity':
        """딕셔너리에서 엔티티 생성"""
        return cls(
            entity_id=data.get('entity_id'),
            company_info=data.get('company_info', {}),
            financial_data=data.get('financial_data', {}),
            risk_assessment=data.get('risk_assessment', {}),
            analysis_result=data.get('analysis_result', {}),
            report_result=data.get('report_result', {}),
            status=data.get('status', 'pending'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )
    
    def update_status(self, new_status: str) -> None:
        """상태 업데이트"""
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def add_analysis_result(self, result: Dict[str, Any]) -> None:
        """분석 결과 추가"""
        self.analysis_result = result
        self.status = "analysis_completed"
        self.updated_at = datetime.utcnow()
    
    def add_risk_assessment(self, assessment: Dict[str, Any]) -> None:
        """위험 평가 결과 추가"""
        self.risk_assessment = assessment
        self.status = "risk_assessed"
        self.updated_at = datetime.utcnow()
    
    def add_report_result(self, report: Dict[str, Any]) -> None:
        """보고서 결과 추가"""
        self.report_result = report
        self.status = "completed"
        self.updated_at = datetime.utcnow()
    
    def is_completed(self) -> bool:
        """완료 상태 확인"""
        return self.status == "completed"
    
    def is_pending(self) -> bool:
        """대기 상태 확인"""
        return self.status == "pending"
    
    def __repr__(self) -> str:
        return f"TCFDEntity(id='{self.entity_id}', status='{self.status}')"

class ClimateRiskEntity:
    """기후 위험 평가 엔티티"""
    
    def __init__(
        self,
        risk_id: Optional[str] = None,
        company_info: Optional[Dict[str, Any]] = None,
        financial_data: Optional[Dict[str, Any]] = None,
        risk_assessment: Optional[Dict[str, Any]] = None,
        climate_scenarios: Optional[Dict[str, Any]] = None,
        risk_score: Optional[float] = None,
        status: str = "pending",
        created_at: Optional[datetime] = None
    ):
        self.risk_id = risk_id or str(uuid.uuid4())
        self.company_info = company_info or {}
        self.financial_data = financial_data or {}
        self.risk_assessment = risk_assessment or {}
        self.climate_scenarios = climate_scenarios or {}
        self.risk_score = risk_score
        self.status = status
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            'risk_id': self.risk_id,
            'company_info': self.company_info,
            'financial_data': self.financial_data,
            'risk_assessment': self.risk_assessment,
            'climate_scenarios': self.climate_scenarios,
            'risk_score': self.risk_score,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ClimateRiskEntity':
        """딕셔너리에서 엔티티 생성"""
        return cls(
            risk_id=data.get('risk_id'),
            company_info=data.get('company_info', {}),
            financial_data=data.get('financial_data', {}),
            risk_assessment=data.get('risk_assessment', {}),
            climate_scenarios=data.get('climate_scenarios', {}),
            risk_score=data.get('risk_score'),
            status=data.get('status', 'pending'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )
    
    def calculate_risk_score(self) -> float:
        """위험 점수 계산"""
        if not self.risk_assessment:
            return 0.0
        
        # 간단한 위험 점수 계산 로직
        risk_factors = self.risk_assessment.get('risk_factors', [])
        if not risk_factors:
            return 0.0
        
        total_score = sum(factor.get('score', 0) for factor in risk_factors)
        return total_score / len(risk_factors)
    
    def update_risk_assessment(self, assessment: Dict[str, Any]) -> None:
        """위험 평가 업데이트"""
        self.risk_assessment = assessment
        self.risk_score = self.calculate_risk_score()
        self.status = "assessed"
    
    def __repr__(self) -> str:
        return f"ClimateRiskEntity(id='{self.risk_id}', score={self.risk_score}, status='{self.status}')"
