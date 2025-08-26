import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from ..llm.llm_service import LLMService
from ..rag.rag_service import RAGService
from .tcfd_model import TCFDInput, TCFDReportRequest, TCFDReportResponse, TCFDRecommendationRequest, TCFDRecommendationResponse, TCFDInputData

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

class TCFDReportService:
    """TCFD 보고서 생성 서비스"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.rag_service = RAGService()
        
        # 데이터베이스 연결 설정
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            try:
                self.engine = create_engine(database_url)
                self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                logger.info("✅ 데이터베이스 연결 성공")
            except Exception as e:
                logger.error(f"❌ 데이터베이스 연결 실패: {e}")
                self.engine = None
                self.SessionLocal = None
        else:
            logger.warning("⚠️ DATABASE_URL이 설정되지 않음")
            self.engine = None
            self.SessionLocal = None

    def get_tcfd_input_data(self, company_name: str) -> Optional[TCFDInputData]:
        """회사명으로 TCFD 입력 데이터 조회"""
        if not self.SessionLocal:
            logger.warning("⚠️ 데이터베이스 연결이 설정되지 않음")
            return None
            
        try:
            with self.SessionLocal() as session:
                result = session.execute(
                    text("SELECT * FROM tcfd_inputs WHERE company_name = :company_name ORDER BY created_at DESC LIMIT 1"),
                    {"company_name": company_name}
                )
                row = result.fetchone()
                
                if row:
                    logger.info(f"✅ {company_name}의 TCFD 입력 데이터 조회 성공")
                    return TCFDInputData(
                        id=row.id,
                        company_name=row.company_name,
                        governance_g1=row.governance_g1,
                        governance_g2=row.governance_g2,
                        strategy_s1=row.strategy_s1,
                        strategy_s2=row.strategy_s2,
                        strategy_s3=row.strategy_s3,
                        risk_management_r1=row.risk_management_r1,
                        risk_management_r2=row.risk_management_r2,
                        risk_management_r3=row.risk_management_r3,
                        metrics_targets_m1=row.metrics_targets_m1,
                        metrics_targets_m2=row.metrics_targets_m2,
                        metrics_targets_m3=row.metrics_targets_m3,
                        created_at=row.created_at,
                        updated_at=row.updated_at
                    )
                else:
                    logger.info(f"ℹ️ {company_name}의 TCFD 입력 데이터가 없음")
                return None
        except Exception as e:
            logger.error(f"❌ TCFD 입력 데이터 조회 실패: {e}")
            return None

    def generate_tcfd_report(self, request: TCFDReportRequest) -> TCFDReportResponse:
        """TCFD 보고서 생성"""
        try:
            # TCFD 권고사항 데이터를 프롬프트에 통합
            prompt = self._create_tcfd_prompt(request)
            
            # RAG를 통한 관련 정보 검색
            rag_context = self._get_rag_context(request)
            
            # 최종 프롬프트 생성
            final_prompt = self._create_final_prompt(prompt, rag_context, request)
            
            # LLM을 통한 보고서 생성
            if request.llm_provider == "openai":
                report_content = self.llm_service.generate_with_openai(final_prompt, request.report_type)
            else:
                report_content = self.llm_service.generate_with_huggingface(final_prompt, request.report_type)
            
            return TCFDReportResponse(
                success=True,
                report_content=report_content,
                generated_at=datetime.now(),
                llm_provider=request.llm_provider,
                report_type=request.report_type
            )
            
        except Exception as e:
            return TCFDReportResponse(
                success=False,
                error_message=str(e),
                generated_at=datetime.now(),
                llm_provider=request.llm_provider,
                report_type=request.report_type
            )
    
    def generate_tcfd_recommendation(self, request: TCFDRecommendationRequest) -> TCFDRecommendationResponse:
        """특정 TCFD 권고사항에 대한 문장 생성 (데이터베이스 데이터 포함)"""
        try:
            logger.info(f"🚀 TCFD 권고사항 생성 시작: {request.company_name} - {request.recommendation_type}")
            
            # 1. 데이터베이스에서 TCFD 입력 데이터 조회
            tcfd_data = self.get_tcfd_input_data(request.company_name)
            
            # 2. RAG를 통한 관련 정보 검색
            rag_context = self._get_recommendation_rag_context(request)
            
            # 3. 프롬프트 생성 (데이터베이스 데이터 포함)
            base_prompt = self._create_recommendation_prompt(request, tcfd_data)
            
            # 4. 최종 프롬프트 생성 (RAG 컨텍스트 포함)
            final_prompt = self._create_recommendation_final_prompt(base_prompt, rag_context, request)
            
            logger.info(f"📝 프롬프트 생성 완료, LLM 호출 시작: {request.llm_provider}")
            
            # 5. LLM을 통한 문장 생성
            if request.llm_provider == "openai":
                generated_text = self.llm_service.generate_with_openai(final_prompt, "recommendation")
            else:
                generated_text = self.llm_service.generate_with_huggingface(final_prompt, "recommendation")
            
            logger.info(f"✅ TCFD 권고사항 생성 완료: {len(generated_text)}자")
            
            return TCFDRecommendationResponse(
                success=True,
                recommendation_type=request.recommendation_type,
                generated_text=generated_text,
                generated_at=datetime.now(),
                llm_provider=request.llm_provider
            )
            
        except Exception as e:
            logger.error(f"❌ TCFD 권고사항 생성 실패: {e}")
            return TCFDRecommendationResponse(
                success=False,
                recommendation_type=request.recommendation_type,
                error_message=str(e),
                generated_at=datetime.now(),
                llm_provider=request.llm_provider
            )
    
    def _create_tcfd_prompt(self, request: TCFDReportRequest) -> str:
        """TCFD 보고서 생성을 위한 프롬프트 생성"""
        tcfd_data = request.tcfd_inputs
        
        prompt = f"""
# TCFD 기후 관련 재무정보 공시 보고서 생성

## 회사 정보
- 회사명: {request.company_name}
- 보고서 연도: {request.report_year}
- 사용자 ID: {tcfd_data.user_id or "정보 없음"}

## TCFD 권고사항 데이터

### 1. 거버넌스 (Governance)
- G1 (거버넌스 항목 1): {tcfd_data.governance_g1 or "정보 없음"}
- G2 (거버넌스 항목 2): {tcfd_data.governance_g2 or "정보 없음"}

### 2. 전략 (Strategy)
- S1 (전략 항목 1): {tcfd_data.strategy_s1 or "정보 없음"}
- S2 (전략 항목 2): {tcfd_data.strategy_s2 or "정보 없음"}
- S3 (전략 항목 3): {tcfd_data.strategy_s3 or "정보 없음"}

### 3. 위험 관리 (Risk Management)
- R1 (위험 관리 항목 1): {tcfd_data.risk_management_r1 or "정보 없음"}
- R2 (위험 관리 항목 2): {tcfd_data.risk_management_r2 or "정보 없음"}
- R3 (위험 관리 항목 3): {tcfd_data.risk_management_r3 or "정보 없음"}

### 4. 지표 및 목표 (Metrics and Targets)
- M1 (지표 및 목표 항목 1): {tcfd_data.metrics_targets_m1 or "정보 없음"}
- M2 (지표 및 목표 항목 2): {tcfd_data.metrics_targets_m2 or "정보 없음"}
- M3 (지표 및 목표 항목 3): {tcfd_data.metrics_targets_m3 or "정보 없음"}

위의 TCFD 권고사항 데이터를 바탕으로 전문적이고 체계적인 기후 관련 재무정보 공시 보고서를 작성해주세요.
"""
        
        if request.report_type == "draft":
            prompt += "\n\n초안 형태로 작성해주세요. 각 섹션별로 명확하게 구분하고, 핵심 내용을 중심으로 작성해주세요."
        else:
            prompt += "\n\n최종 보고서 형태로 작성해주세요. 전문적이고 공식적인 톤으로 작성하고, 모든 섹션을 상세하게 작성해주세요."
        
        return prompt
    
    def _create_recommendation_prompt(self, request: TCFDRecommendationRequest, tcfd_data: Optional[TCFDInputData] = None) -> str:
        """특정 TCFD 권고사항에 대한 프롬프트 생성 (데이터베이스 데이터 포함)"""
        
        # 권고사항별 설명 매핑
        recommendation_descriptions = {
            "g1": "기후 관련 위험과 기회에 대한 이사회 감독",
            "g2": "기후 관련 위험과 기회에 대한 경영진 역할",
            "s1": "기후 관련 위험과 기회의 비즈니스 영향",
            "s2": "전략적 영향의 실제 잠재적 영향",
            "s3": "기후 시나리오 분석",
            "r1": "기후 관련 위험 식별 및 평가 프로세스",
            "r2": "위험 관리 프로세스 통합",
            "r3": "위험 관리 프로세스",
            "m1": "기후 관련 위험 평가 지표",
            "m2": "기후 관련 기회 평가 지표",
            "m3": "기후 관련 목표 설정"
        }
        
        description = recommendation_descriptions.get(request.recommendation_type, "TCFD 권고사항")
        
        prompt = f"""
# TCFD 권고사항 문장 생성

## 회사 정보
- 회사명: {request.company_name}

## 권고사항 정보
- 권고사항 유형: {request.recommendation_type.upper()}
- 권고사항 설명: {description}

## 사용자 입력 데이터
{request.user_input}

## 데이터베이스에 저장된 TCFD 입력 데이터
"""
        
        # 데이터베이스 데이터가 있으면 추가
        if tcfd_data:
            prompt += f"""
### 거버넌스 (Governance)
- G1: {tcfd_data.governance_g1 or '입력 없음'}
- G2: {tcfd_data.governance_g2 or '입력 없음'}

### 전략 (Strategy)
- S1: {tcfd_data.strategy_s1 or '입력 없음'}
- S2: {tcfd_data.strategy_s2 or '입력 없음'}
- S3: {tcfd_data.strategy_s3 or '입력 없음'}

### 위험 관리 (Risk Management)
- R1: {tcfd_data.risk_management_r1 or '입력 없음'}
- R2: {tcfd_data.risk_management_r2 or '입력 없음'}
- R3: {tcfd_data.risk_management_r3 or '입력 없음'}

### 지표 및 목표 (Metrics & Targets)
- M1: {tcfd_data.metrics_targets_m1 or '입력 없음'}
- M2: {tcfd_data.metrics_targets_m2 or '입력 없음'}
- M3: {tcfd_data.metrics_targets_m3 or '입력 없음'}
"""
        else:
            prompt += "\n데이터베이스에 저장된 TCFD 입력 데이터가 없습니다.\n"

        prompt += """

## 요청사항
위의 정보를 바탕으로 TCFD 프레임워크에 맞는 전문적이고 체계적인 문장을 작성해주세요.

## 작성 가이드라인
1. TCFD 국제 표준에 부합하는 전문적인 문장으로 작성
2. 한국 기업 문화와 규제 환경을 고려
3. ESG/TCFD 전문 용어를 적절히 사용
4. 구체적이고 실행 가능한 내용으로 구성
5. 사용자가 입력한 데이터의 핵심 내용을 반영
6. 데이터베이스에 저장된 TCFD 입력 데이터를 참고하여 일관성 있는 문장 작성
7. TCFD 국제 표준에 부합하는 내용
8. 200-300자 내외로 작성
9. 공식적이고 객관적인 톤

위의 가이드라인을 따라 전문적인 TCFD 권고사항 문장을 작성해주세요.
"""
        
        if request.context:
            prompt += f"\n\n## 추가 컨텍스트\n{request.context}"
        
        return prompt
    
    def _get_rag_context(self, request: TCFDReportRequest) -> str:
        """TCFD 보고서 생성을 위한 RAG 컨텍스트 검색"""
        try:
            # TCFD 관련 검색 쿼리
            query = f"TCFD 기후 관련 재무정보 공시 {request.company_name} 기후변화 위험 기회"
            
            # RAG 서비스를 통한 관련 정보 검색
            if request.llm_provider == "openai":
                search_results = self.rag_service.search_openai(query, top_k=5)
            else:
                search_results = self.rag_service.search_huggingface(query, top_k=5)
            
            # 검색 결과를 컨텍스트로 변환
            context = "\n\n".join([result.content for result in search_results])
            return context
            
        except Exception as e:
            # RAG 검색 실패 시 빈 컨텍스트 반환
            return ""
    
    def _get_recommendation_rag_context(self, request: TCFDRecommendationRequest) -> str:
        """특정 TCFD 권고사항에 대한 RAG 컨텍스트 검색"""
        try:
            # 권고사항별 검색 쿼리
            query = f"TCFD {request.recommendation_type} {request.company_name} 기후변화"
            
            # RAG 서비스를 통한 관련 정보 검색
            if request.llm_provider == "openai":
                search_results = self.rag_service.search_openai(query, top_k=3)
            else:
                search_results = self.rag_service.search_huggingface(query, top_k=3)
            
            # 검색 결과를 컨텍스트로 변환
            context = "\n\n".join([result.content for result in search_results])
            return context
            
        except Exception as e:
            # RAG 검색 실패 시 빈 컨텍스트 반환
            return ""
    
    def _create_final_prompt(self, base_prompt: str, rag_context: str, request: TCFDReportRequest) -> str:
        """최종 프롬프트 생성 (RAG 컨텍스트 포함)"""
        if rag_context:
            final_prompt = f"{base_prompt}\n\n## 관련 참고 자료\n{rag_context}\n\n위의 참고 자료를 참고하여 더욱 정확하고 전문적인 보고서를 작성해주세요."
        else:
            final_prompt = base_prompt
        
        return final_prompt
    
    def _create_recommendation_final_prompt(self, base_prompt: str, rag_context: str, request: TCFDRecommendationRequest) -> str:
        """권고사항별 최종 프롬프트 생성 (RAG 컨텍스트 포함)"""
        if rag_context and rag_context.strip():
            final_prompt = f"""{base_prompt}

## 관련 참고 자료 (RAG 검색 결과)
{rag_context}

## 추가 지침
위의 참고 자료를 참고하여 더욱 정확하고 전문적인 권고사항 문장을 작성해주세요. 
참고 자료의 내용과 사용자 입력 데이터를 적절히 조합하여 일관성 있는 문장을 만들어주세요.
"""
        else:
            final_prompt = base_prompt
        
        return final_prompt
