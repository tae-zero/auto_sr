from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseLLMService(ABC):
    """LLM 서비스의 기본 추상 클래스"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        logger.info(f"{service_name} LLM 서비스 초기화")
    
    @abstractmethod
    def generate_draft_section(self, question: str, context: str, section: str, style_guide: str = "") -> str:
        """섹션별 초안을 생성합니다."""
        pass
    
    @abstractmethod
    def polish_text(self, text: str, tone: str = "공식적", style_guide: str = "") -> str:
        """텍스트를 윤문합니다."""
        pass
    
    def _create_draft_prompt(self, question: str, context: str, section: str, style_guide: str = "") -> str:
        """초안 생성 프롬프트를 생성합니다."""
        prompt = f"""다음 '근거'를 바탕으로 ESG 보고서의 섹션 초안을 작성하세요.

- [중요] 근거 문장을 인용할 때는 [1], [2]처럼 번호로 표시
- 두괄식 요약 → 핵심 bullet 3~5개 → 상세 설명 순서
- ESG/회계 전문 용어, 수치, 기간을 정확히 유지
- 외부 사실 추정/창작 금지, 근거 없는 수치 생성 금지
- 문체: 공식적·객관적, 존칭/구어체 금지

[섹션] {section}
[질문] {question}
[근거] {context}

{style_guide if style_guide else ""}

초안:"""
        return prompt
    
    def _create_polish_prompt(self, text: str, tone: str = "공식적", style_guide: str = "") -> str:
        """윤문 프롬프트를 생성합니다."""
        prompt = f"""아래 텍스트를 윤문하세요.

- 용어/서식 일관화(ESG/회계 기준)
- 중복/군더더기 제거, 문장 간 논리 연결 강화
- 숫자/단위/연도 표기 통일
- 어조: {tone}

[스타일 가이드]
{style_guide if style_guide else "ESG/회계 전문용어 유지, 불필요한 수식어 제거, 한국어 문체 통일"}

[원문]
{text}

윤문된 텍스트:"""
        return prompt
    
    def get_service_info(self) -> Dict[str, Any]:
        """서비스 정보를 반환합니다."""
        return {
            "service_name": self.service_name,
            "type": "llm_service"
        }
