import openai
import logging
from typing import Optional
from ...common.config import (
    OPENAI_API_KEY, OPENAI_MODEL, 
    OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
)
from .base_llm_service import BaseLLMService

logger = logging.getLogger(__name__)

class OpenAILLMService(BaseLLMService):
    """OpenAI 기반 LLM 서비스"""
    
    def __init__(self):
        super().__init__("OpenAI LLM Service")
        
        # OpenAI API 키 설정
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
            logger.info("OpenAI API 키 설정 완료")
        else:
            logger.warning("OpenAI API 키가 설정되지 않음")
    
    def generate_draft_section(self, question: str, context: str, section: str, style_guide: str = "") -> str:
        """섹션별 초안을 생성합니다."""
        try:
            prompt = self._create_draft_prompt(question, context, section, style_guide)
            
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "당신은 ESG 보고서 작성 전문가입니다. 주어진 근거를 바탕으로 정확하고 전문적인 초안을 작성해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=OPENAI_MAX_TOKENS,
                temperature=OPENAI_TEMPERATURE
            )
            
            content = response.choices[0].message.content
            logger.info(f"OpenAI 초안 생성 완료: {section}")
            return content
            
        except Exception as e:
            logger.error(f"OpenAI 초안 생성 실패: {e}")
            raise
    
    def polish_text(self, text: str, tone: str = "공식적", style_guide: str = "") -> str:
        """텍스트를 윤문합니다."""
        try:
            prompt = self._create_polish_prompt(text, tone, style_guide)
            
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "당신은 ESG 보고서 윤문 전문가입니다. 주어진 텍스트를 전문적이고 일관성 있게 윤문해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=OPENAI_MAX_TOKENS,
                temperature=OPENAI_TEMPERATURE
            )
            
            content = response.choices[0].message.content
            logger.info("OpenAI 윤문 완료")
            return content
            
        except Exception as e:
            logger.error(f"OpenAI 윤문 실패: {e}")
            raise
