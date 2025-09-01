import requests
import logging
import os
from typing import Optional
from ...common.config import (
    HF_API_TOKEN, HF_MODEL, HF_API_URL, HF_LOCAL_MODEL_PATH
)
from .base_llm_service import BaseLLMService

logger = logging.getLogger(__name__)

class HuggingFaceLLMService(BaseLLMService):
    """Hugging Face 기반 LLM 서비스 (코알파, RoLA 학습용)"""
    
    def __init__(self):
        super().__init__("Hugging Face LLM Service")
        
        # 모델 로딩 방식 결정
        self.use_local_model = HF_LOCAL_MODEL_PATH and HF_LOCAL_MODEL_PATH.strip()
        self.use_inference_endpoint = HF_API_URL and HF_API_URL.strip() and not self.use_local_model
        
        logger.info(f"모델 로딩 방식 결정:")
        logger.info(f"  - use_local_model: {self.use_local_model}")
        logger.info(f"  - use_inference_endpoint: {self.use_inference_endpoint}")
        logger.info(f"  - HF_API_URL: {HF_API_URL}")
        
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        if self.use_local_model:
            # 로컬 모델 로딩
            logger.info("로컬 모델 로딩 방식 선택")
            self._load_local_model()
        elif self.use_inference_endpoint:
            # Hugging Face Inference Endpoint 사용
            logger.info("Hugging Face Inference Endpoint 사용 - 모델 다운로드 없음")
            self.use_local_model = False
        else:
            # Hugging Face Hub에서 직접 모델 로딩
            logger.info("Hugging Face Hub 직접 모델 로딩 방식 선택")
            self._load_hf_hub_model()
    
    def _load_hf_hub_model(self):
        """Hugging Face Hub에서 모델을 직접 로딩합니다. (Inference Endpoint 사용으로 인해 비활성화)"""
        logger.info("Inference Endpoint 사용으로 인해 모델 다운로드 비활성화")
        self.use_local_model = False
    
    def _load_local_model(self):
        """로컬 모델을 로드합니다. (Inference Endpoint 사용으로 인해 비활성화)"""
        logger.info("Inference Endpoint 사용으로 인해 로컬 모델 로딩 비활성화")
        self.use_local_model = False
    
    def _call_hf_inference_endpoint(self, prompt: str) -> str:
        """Hugging Face Inference Endpoint를 호출하여 텍스트를 생성합니다."""
        try:
            # API 토큰 확인
            if not HF_API_TOKEN:
                logger.error("HF_API_TOKEN이 설정되지 않음")
                return "[오류] Hugging Face API 토큰이 설정되지 않았습니다."
            
            # 프롬프트 전처리
            formatted_prompt = self._format_prompt_for_model(prompt)
            
            headers = {
                "Authorization": f"Bearer {HF_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            # Inference Endpoint URL 직접 사용
            response = requests.post(
                HF_API_URL,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    # 프롬프트 부분 제거하고 생성된 텍스트만 반환
                    if formatted_prompt in generated_text:
                        generated_text = generated_text.replace(formatted_prompt, '').strip()
                    return generated_text
                elif isinstance(result, dict):
                    generated_text = result.get("generated_text", "")
                    if formatted_prompt in generated_text:
                        generated_text = generated_text.replace(formatted_prompt, '').strip()
                    return generated_text
                else:
                    return str(result)
            else:
                logger.error(f"Hugging Face Inference Endpoint 호출 실패: {response.status_code} - {response.text}")
                logger.error(f"요청 URL: {HF_API_URL}")
                logger.error(f"요청 헤더: {headers}")
                logger.error(f"요청 페이로드: {payload}")
                return f"[API 오류] Hugging Face Inference Endpoint 호출에 실패했습니다. (상태 코드: {response.status_code}) - {response.text[:200]}"
                
        except Exception as e:
            logger.error(f"Hugging Face Inference Endpoint 호출 중 오류: {e}")
            return f"[연결 오류] Hugging Face Inference Endpoint 연결에 실패했습니다: {str(e)}"
    
    def _call_hf_api(self, prompt: str) -> str:
        """Hugging Face API를 호출합니다. (기존 방식 보존)"""
        # API 키가 없으면 fallback 메시지 반환
        if not HF_API_TOKEN:
            logger.warning("Hugging Face API 토큰이 설정되지 않아 fallback 모드로 동작")
            return f"[Hugging Face API 미설정] {prompt[:100]}...에 대한 응답을 생성할 수 없습니다. API 토큰을 설정해주세요."
        
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
                return f"[API 오류] Hugging Face API 호출에 실패했습니다. (상태 코드: {response.status_code})"
                
        except Exception as e:
            logger.error(f"Hugging Face API 호출 중 오류: {e}")
            return f"[연결 오류] Hugging Face API 연결에 실패했습니다: {str(e)}"
    
    def _generate_with_loaded_model(self, prompt: str) -> str:
        """로딩된 모델로 텍스트를 생성합니다. (Inference Endpoint 사용으로 인해 비활성화)"""
        logger.warning("로딩된 모델 사용 시도 - Inference Endpoint로 fallback")
        return self._call_hf_inference_endpoint(prompt)
    
    def _format_prompt_for_model(self, prompt: str) -> str:
        """모델용 프롬프트를 포맷팅합니다."""
        # TCFD 전문가 프롬프트 추가
        system_prompt = "당신은 TCFD 기후 관련 재무정보 공시 보고서 작성 전문가입니다. 전문적이고 체계적인 보고서를 작성해주세요."
        return f"{system_prompt}\n\n{prompt}"
    
    def _generate_text(self, prompt: str) -> str:
        """텍스트 생성 방식에 따라 적절한 메서드를 호출합니다."""
        if self.use_inference_endpoint:
            # Hugging Face Inference Endpoint 사용
            return self._call_hf_inference_endpoint(prompt)
        elif self.pipeline:
            # 로딩된 모델 사용
            return self._generate_with_loaded_model(prompt)
        else:
            # 기존 API 호출 방식
            return self._call_hf_api(prompt)
    
    def generate_draft_section(self, question: str, context: str, section: str, style_guide: str = "") -> str:
        """섹션별 초안을 생성합니다. (기존 메서드 보존)"""
        try:
            prompt = self._create_draft_prompt(question, context, section, style_guide)
            
            content = self._generate_text(prompt)
            logger.info(f"Hugging Face 초안 생성 완료: {section}")
            return content
            
        except Exception as e:
            logger.error(f"Hugging Face 초안 생성 실패: {e}")
            return f"[오류] {section} 섹션 초안 생성에 실패했습니다: {str(e)}"
    
    def polish_text(self, text: str, tone: str = "공식적", style_guide: str = "") -> str:
        """텍스트를 윤문합니다. (기존 메서드 보존)"""
        try:
            prompt = self._create_polish_prompt(text, tone, style_guide)
            
            content = self._generate_text(prompt)
            logger.info("Hugging Face 윤문 완료")
            return content
            
        except Exception as e:
            logger.error(f"Hugging Face 윤문 실패: {e}")
            return f"[오류] 텍스트 윤문에 실패했습니다: {str(e)}"
