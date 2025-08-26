import os
import json
from datetime import datetime
from typing import Dict, Any
from ..llm.llm_service import LLMService
from ..rag.rag_service import RAGService
from .tcfd_model import TCFDInput, TCFDReportRequest, TCFDReportResponse

class TCFDReportService:
    """TCFD 보고서 생성 서비스"""
    
    def __init__(self):
        self.llm_service = LLMService()
        self.rag_service = RAGService()
        
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
    
    def _create_tcfd_prompt(self, request: TCFDReportRequest) -> str:
        """TCFD 권고사항 데이터를 기반으로 프롬프트 생성 (실제 테이블 구조 기반)"""
        
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
            prompt += "\n\n## 요구사항\n- 초안 형태로 작성 (개요 및 주요 내용 위주)\n- 전문적이면서도 이해하기 쉽게 작성\n- 각 섹션별로 명확하게 구분하여 작성\n- 입력된 데이터를 바탕으로 구체적인 내용 작성"
        else:
            prompt += "\n\n## 요구사항\n- 완성된 보고서 형태로 작성\n- 전문적이고 상세한 내용 포함\n- 실행 가능한 구체적 제안 포함\n- 국제 표준에 부합하는 형식으로 작성\n- 입력된 데이터를 바탕으로 상세한 분석 및 제안 작성"
        
        return prompt
    
    def _get_rag_context(self, request: TCFDReportRequest) -> str:
        """RAG를 통한 관련 정보 검색"""
        try:
            # TCFD 관련 질의로 RAG 검색
            query = f"TCFD 기후 관련 재무정보 공시 {request.company_name} {request.report_year}"
            rag_results = self.rag_service.search(query, top_k=5)
            
            if rag_results:
                context = "## 관련 참고 자료\n"
                for i, result in enumerate(rag_results, 1):
                    context += f"{i}. {result['content'][:200]}...\n\n"
                return context
            else:
                return ""
        except Exception as e:
            print(f"RAG 검색 오류: {e}")
            return ""
    
    def _create_final_prompt(self, tcfd_prompt: str, rag_context: str, request: TCFDReportRequest) -> str:
        """최종 프롬프트 생성"""
        
        final_prompt = f"""
{tcfd_prompt}

{rag_context}

## 작성 지침
1. 위의 TCFD 권고사항 데이터를 기반으로 작성
2. {rag_context if rag_context else "일반적인 TCFD 가이드라인을 참고하여"} 작성
3. {request.report_type} 형태로 작성
4. 한국어로 작성
5. 전문적이고 체계적인 구조로 작성
6. 실행 가능한 구체적 제안 포함
7. 입력된 데이터가 있는 항목은 해당 내용을 반영하여 구체적으로 작성
8. 입력된 데이터가 없는 항목은 일반적인 가이드라인을 제시

위의 정보를 바탕으로 TCFD 기후 관련 재무정보 공시 보고서를 작성해주세요.
"""
        
        return final_prompt
