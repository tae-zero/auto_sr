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
            
            logger.info(f"API 토큰 확인: {HF_API_TOKEN[:10]}...")
            
            # 프롬프트 전처리
            formatted_prompt = self._format_prompt_for_model(prompt)
            
            headers = {
                "Authorization": f"Bearer {HF_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            # 기본 페이로드 (보수적 설정으로 조정)
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": 150,      # 더 짧은 응답으로 안정성 향상
                    "temperature": 0.2,         # 매우 일관된 응답
                    "do_sample": True,
                    "return_full_text": False,
                    "top_p": 0.7,              # 더 보수적인 다양성
                    "repetition_penalty": 1.3,  # 반복 방지 강화
                    "pad_token_id": 2,          # <|endoftext|> 토큰 ID
                    "eos_token_id": 2           # <|endoftext|> 토큰 ID
                }
            }
            
            # Endpoint 헬스체크 먼저 시도
            try:
                health_response = requests.get(HF_API_URL, timeout=10)
                logger.info(f"Endpoint 헬스체크: {health_response.status_code}")
                
                # 모델 준비 상태 확인
                if health_response.status_code == 200:
                    try:
                        health_data = health_response.json()
                        logger.info(f"헬스체크 응답: {health_data}")
                        if "error" in health_data:
                            logger.warning(f"모델 준비 중: {health_data['error']}")
                    except:
                        logger.info(f"헬스체크 응답 텍스트: {health_response.text}")
                elif health_response.status_code == 401:
                    logger.error("인증 실패 - API 토큰 확인 필요")
                elif health_response.status_code == 503:
                    logger.warning("서비스 일시적 사용 불가 - 모델 로딩 중일 수 있음")
                else:
                    logger.warning(f"헬스체크 예상치 못한 상태: {health_response.status_code}")
                    
            except Exception as e:
                logger.warning(f"Endpoint 헬스체크 실패: {e}")
            
            # Inference Endpoint URL 직접 사용 (CPU 환경을 고려한 긴 타임아웃)
            response = requests.post(
                HF_API_URL,
                headers=headers,
                json=payload,
                timeout=120  # CPU 환경에서는 더 긴 타임아웃 필요
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"응답 결과: {result}")
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                    logger.info(f"생성된 텍스트: {generated_text}")
                    # 프롬프트 부분 제거하고 생성된 텍스트만 반환
                    if formatted_prompt in generated_text:
                        generated_text = generated_text.replace(formatted_prompt, '').strip()
                    
                    # 특수 토큰 제거
                    generated_text = generated_text.replace('<|sep|>', '').replace('<|endoftext|>', '').strip()
                    
                    return generated_text
                elif isinstance(result, dict):
                    generated_text = result.get("generated_text", "")
                    if formatted_prompt in generated_text:
                        generated_text = generated_text.replace(formatted_prompt, '').strip()
                    
                    # 특수 토큰 제거
                    generated_text = generated_text.replace('<|sep|>', '').replace('<|endoftext|>', '').strip()
                    
                    return generated_text
                else:
                    return str(result)
            else:
                logger.error(f"Hugging Face Inference Endpoint 호출 실패: {response.status_code} - {response.text}")
                logger.error(f"요청 URL: {HF_API_URL}")
                logger.error(f"요청 헤더: {headers}")
                logger.error(f"요청 페이로드: {payload}")
                
                # 500 오류 시 더 자세한 정보 로깅
                if response.status_code == 500:
                    logger.error("=== 500 오류 상세 분석 ===")
                    logger.error(f"응답 헤더: {dict(response.headers)}")
                    logger.error(f"응답 크기: {len(response.content)} bytes")
                    try:
                        error_detail = response.json()
                        logger.error(f"오류 상세: {error_detail}")
                    except:
                        logger.error(f"응답 텍스트: {response.text}")
                    logger.error("========================")
                
                # Inference Endpoint 실패 시 Hugging Face API로 fallback
                logger.info("Inference Endpoint 실패 - Hugging Face API로 fallback 시도")
                fallback_result = self._call_hf_api_fallback(prompt)
                
                # Fallback도 실패하면 기본 메시지 반환
                if "실패" in fallback_result or "오류" in fallback_result:
                    return f"[Inference Endpoint 오류] {response.status_code} - {response.text[:100]}... (Fallback도 실패)"
                
                return fallback_result
                
        except Exception as e:
            logger.error(f"Hugging Face Inference Endpoint 호출 중 오류: {e}")
            return f"[연결 오류] Hugging Face Inference Endpoint 연결에 실패했습니다: {str(e)}"
    
    def _call_hf_api_fallback(self, prompt: str) -> str:
        """Hugging Face API로 fallback합니다."""
        try:
            # Hugging Face API URL 사용 (실제 존재하는 모델로 테스트)
            api_url = "https://api-inference.huggingface.co/models/EleutherAI/polyglot-ko-3.8b"
            
            headers = {
                "Authorization": f"Bearer {HF_API_TOKEN}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.2,
                    "do_sample": True,
                    "return_full_text": False,
                    "top_p": 0.7,
                    "repetition_penalty": 1.3,
                    "pad_token_id": 2,
                    "eos_token_id": 2
                }
            }
            
            response = requests.post(
                api_url,
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
                logger.error(f"Hugging Face API fallback도 실패: {response.status_code} - {response.text}")
                return f"[Fallback 실패] Hugging Face API 호출도 실패했습니다. (상태 코드: {response.status_code})"
                
        except Exception as e:
            logger.error(f"Hugging Face API fallback 중 오류: {e}")
            return f"[Fallback 오류] Hugging Face API 연결에 실패했습니다: {str(e)}"
    
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
        # 극도로 단순화된 프롬프트 (32개 레이어 모델의 안정성 고려)
        system_prompt = """한국어로 문장을 작성해주세요.<|sep|>"""
        
        # 입력 데이터 길이 제한 (더 엄격하게)
        if len(prompt) > 500:  # 더 짧게 제한
            prompt = prompt[:500] + "..."
        
        return f"{system_prompt}\n\n{prompt}<|sep|>"
    
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
