import os
import json
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMService:
    """LLM 서비스 - OpenAI와 Hugging Face API 지원"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.hf_api_token = os.getenv('HF_API_TOKEN')
        self.hf_api_url = os.getenv('HF_API_URL', 'https://api-inference.huggingface.co/models/EleutherAI/polyglot-ko-3.8b')
        
    def generate_with_openai(self, prompt: str, report_type: str = "draft") -> str:
        """OpenAI API를 사용하여 텍스트 생성"""
        try:
            if not self.openai_api_key:
                logger.error("OpenAI API 키가 설정되지 않았습니다")
                return "OpenAI API 키가 설정되지 않았습니다."
            
            # OpenAI API 호출
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
                "messages": [
                    {
                        "role": "system",
                        "content": f"당신은 TCFD 기후 관련 재무정보 공시 보고서 작성 전문가입니다. {report_type} 형태로 전문적이고 체계적인 보고서를 작성해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": int(os.getenv('OPENAI_MAX_TOKENS', '2000')),
                "temperature": float(os.getenv('OPENAI_TEMPERATURE', '0.3'))
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                logger.info("OpenAI API 호출 성공")
                return content
            else:
                logger.error(f"OpenAI API 호출 실패: {response.status_code} - {response.text}")
                return f"OpenAI API 호출 실패: {response.status_code}"
                
        except Exception as e:
            logger.error(f"OpenAI API 호출 중 오류 발생: {str(e)}")
            return f"OpenAI API 호출 중 오류 발생: {str(e)}"
    
    def generate_with_huggingface(self, prompt: str, report_type: str = "draft") -> str:
        """Hugging Face API를 사용하여 텍스트 생성 (로컬 모델 또는 API 호출)"""
        try:
            # HuggingFaceLLMService 인스턴스 생성하여 사용
            from .huggingface_llm_service import HuggingFaceLLMService
            hf_service = HuggingFaceLLMService()
            
            # 시스템 메시지가 포함된 프롬프트 생성
            system_message = f"당신은 TCFD 기후 관련 재무정보 공시 보고서 작성 전문가입니다. {report_type} 형태로 전문적이고 체계적인 보고서를 작성해주세요."
            full_prompt = f"{system_message}\n\n{prompt}"
            
            # HuggingFaceLLMService의 _generate_text 메서드 사용
            content = hf_service._generate_text(full_prompt)
            
            logger.info("Hugging Face 텍스트 생성 완료")
            return content
                
        except Exception as e:
            logger.error(f"Hugging Face 텍스트 생성 중 오류 발생: {str(e)}")
            return f"Hugging Face 텍스트 생성 중 오류 발생: {str(e)}"
