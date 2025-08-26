import requests
import logging
from typing import Optional
from ...common.config import (
    HF_API_TOKEN, HF_MODEL, HF_API_URL
)
from .base_llm_service import BaseLLMService

logger = logging.getLogger(__name__)

class HuggingFaceLLMService(BaseLLMService):
    """Hugging Face 기반 LLM 서비스 (코알파, RoLA 학습용)"""
    
    def __init__(self):
        super().__init__("Hugging Face LLM Service")
        
        # Hugging Face API 설정 검증
        if not HF_API_TOKEN:
            logger.warning("Hugging Face API 토큰이 설정되지 않음")
        if not HF_API_URL:
            logger.warning("Hugging Face API URL이 설정되지 않음")
    
    def _call_hf_api(self, prompt: str) -> str:
        """Hugging Face API를 호출합니다."""
        try:
            headers = {
                "Authorization": f"Bearer {HF_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                HF_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    return result.get("generated_text", "")
                else:
                    return str(result)
            else:
                logger.error(f"Hugging Face API 호출 실패: {response.status_code} - {response.text}")
                raise Exception(f"API 호출 실패: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Hugging Face API 호출 중 오류: {e}")
            raise
    
    def generate_draft_section(self, question: str, context: str, section: str, style_guide: str = "") -> str:
        """섹션별 초안을 생성합니다."""
        try:
            prompt = self._create_draft_prompt(question, context, section, style_guide)
            
            content = self._call_hf_api(prompt)
            logger.info(f"Hugging Face 초안 생성 완료: {section}")
            return content
            
        except Exception as e:
            logger.error(f"Hugging Face 초안 생성 실패: {e}")
            raise
    
    def polish_text(self, text: str, tone: str = "공식적", style_guide: str = "") -> str:
        """텍스트를 윤문합니다."""
        try:
            prompt = self._create_polish_prompt(text, tone, style_guide)
            
            content = self._call_hf_api(prompt)
            logger.info("Hugging Face 윤문 완료")
            return content
            
        except Exception as e:
            logger.error(f"Hugging Face 윤문 실패: {e}")
            raise
