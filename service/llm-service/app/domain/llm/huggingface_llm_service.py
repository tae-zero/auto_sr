import requests
import logging
import os
from typing import Optional
from ...common.config import (
    HF_API_TOKEN, HF_MODEL, HF_API_URL, HF_LOCAL_MODEL_PATH
)
from .base_llm_service import BaseLLMService
import re

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
            
            # 모델 특성에 최적화된 파라미터 (사용자 학습 모델 기준)
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": 256,      # 모델 최대 길이(2048) 고려하여 조정
                    "temperature": 0.7,         # 창의성과 일관성 균형
                    "do_sample": True,
                    "return_full_text": False,
                    "top_p": 0.9,              # 토큰 선택 범위
                    "repetition_penalty": 1.1,  # 반복 방지
                    "no_repeat_ngram_size": 3,  # 3-gram 반복 방지
                    "early_stopping": True,     # 조기 종료
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
                    
                    # 특수 토큰 및 반복 문자 제거
                    generated_text = generated_text.replace('<|sep|>', '').replace('<|endoftext|>', '').strip()
                    # ################# 같은 반복 문자 제거
                    generated_text = re.sub(r'#{3,}', '', generated_text)  # 3개 이상의 # 제거
                    generated_text = re.sub(r'[=]{3,}', '', generated_text)  # 3개 이상의 = 제거
                    generated_text = re.sub(r'[-]{3,}', '', generated_text)  # 3개 이상의 - 제거
                    generated_text = re.sub(r'[*]{3,}', '', generated_text)  # 3개 이상의 * 제거
                    generated_text = re.sub(r'[~]{3,}', '', generated_text)  # 3개 이상의 ~ 제거
                    generated_text = generated_text.strip()
                    
                    return generated_text
                elif isinstance(result, dict):
                    generated_text = result.get("generated_text", "")
                    if formatted_prompt in generated_text:
                        generated_text = generated_text.replace(formatted_prompt, '').strip()
                    
                    # 특수 토큰 및 반복 문자 제거
                    generated_text = generated_text.replace('<|sep|>', '').replace('<|endoftext|>', '').strip()
                    # ################# 같은 반복 문자 제거
                    generated_text = re.sub(r'#{3,}', '', generated_text)  # 3개 이상의 # 제거
                    generated_text = re.sub(r'[=]{3,}', '', generated_text)  # 3개 이상의 = 제거
                    generated_text = re.sub(r'[-]{3,}', '', generated_text)  # 3개 이상의 - 제거
                    generated_text = re.sub(r'[*]{3,}', '', generated_text)  # 3개 이상의 * 제거
                    generated_text = re.sub(r'[~]{3,}', '', generated_text)  # 3개 이상의 ~ 제거
                    generated_text = generated_text.strip()
                    
                    return generated_text
                else:
                    return str(result)
            else:
                logger.error(f"Hugging Face Inference Endpoint 호출 실패: {response.status_code} - {response.text}")
                logger.error(f"요청 URL: {HF_API_URL}")
                logger.error(f"요청 헤더: {headers}")
                logger.error(f"요청 페이로드: {payload}")
                
                # 특수 오류 처리 (paused endpoint 등)
                if response.status_code == 400:
                    try:
                        error_data = response.json()
                        if "error" in error_data and "paused" in error_data["error"].lower():
                            logger.error("Inference Endpoint가 일시정지 상태입니다.")
                            return "[Inference Endpoint 일시정지] 모델이 일시정지 상태입니다. Hugging Face 웹사이트에서 엔드포인트를 재시작해주세요."
                    except:
                        pass
                
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
                    "max_new_tokens": 200,      # fallback용으로 적당한 길이
                    "temperature": 0.7,         # 일관성 있는 파라미터
                    "do_sample": True,
                    "return_full_text": False,
                    "top_p": 0.9,              # 일관성 있는 파라미터
                    "repetition_penalty": 1.1,  # 일관성 있는 파라미터
                    "no_repeat_ngram_size": 3,  # 반복 방지
                    "early_stopping": True,     # 조기 종료
                    "pad_token_id": 2,          # <|endoftext|> 토큰 ID
                    "eos_token_id": 2           # <|endoftext|> 토큰 ID
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
        """모델용 프롬프트를 포맷팅합니다. (사용자 학습 모델 최적화)"""
        # 특수 토큰 충돌 방지를 위해 <|sep|> 토큰은 사용하지 않음
        # 하지만 효과적인 프롬프트 구조는 유지
        
        # 입력 데이터 길이 제한 (모델 최대 길이 2048 토큰 고려)
        if len(prompt) > 600:  # 토큰 길이 제한을 고려하여 조정
            prompt = prompt[:600] + "..."
        
        # 학습된 모델에 최적화된 프롬프트 구조
        system_instruction = "다음 질문에 대해 한국어로 명확하고 구체적으로 답변해주세요."
        
        # 효과적인 프롬프트 구조 (특수 토큰 없이)
        formatted_prompt = f"{system_instruction}\n\n질문: {prompt}\n\n답변:"
        
        return formatted_prompt
    
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
    
    def _create_draft_prompt(self, question: str, context: str, section: str, style_guide: str = "") -> str:
        """초안 생성 프롬프트를 생성합니다. (사용자 학습 모델 최적화)"""
        # 입력 길이 제한 (토큰 제한 고려)
        if len(context) > 800:
            context = context[:800] + "..."
        if len(question) > 200:
            question = question[:200] + "..."
        
        # 학습된 모델에 최적화된 프롬프트 구조
        prompt = f"""다음 근거를 바탕으로 ESG 보고서의 {section} 섹션 초안을 작성해주세요.

요구사항:
- 근거 문장 인용 시 [1], [2] 번호로 표시
- 두괄식 요약 → 핵심 bullet 3~5개 → 상세 설명 순서
- ESG/회계 전문 용어와 수치를 정확히 유지
- 외부 사실 추정이나 창작 금지
- 공식적이고 객관적인 문체 사용

질문: {question}

근거: {context}

{style_guide if style_guide else ""}

초안:"""
        return prompt
    
    def _create_polish_prompt(self, text: str, tone: str = "공식적", style_guide: str = "") -> str:
        """윤문 프롬프트를 생성합니다. (사용자 학습 모델 최적화)"""
        # 입력 길이 제한
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        # 학습된 모델에 최적화된 프롬프트 구조
        prompt = f"""아래 텍스트를 {tone}한 어조로 윤문해주세요.

요구사항:
- ESG/회계 전문용어 일관성 유지
- 중복이나 군더더기 제거
- 문장 간 논리적 연결 강화
- 숫자, 단위, 연도 표기 통일

{style_guide if style_guide else "ESG/회계 전문용어 유지, 불필요한 수식어 제거, 한국어 문체 통일"}

원문: {text}

윤문된 텍스트:"""
        return prompt

    def generate_draft_section(self, question: str, context: str, section: str, style_guide: str = "") -> str:
        """섹션별 초안을 생성합니다."""
        try:
            prompt = self._create_draft_prompt(question, context, section, style_guide)
            
            content = self._generate_text(prompt)
            logger.info(f"Hugging Face 초안 생성 완료: {section}")
            return content
            
        except Exception as e:
            logger.error(f"Hugging Face 초안 생성 실패: {e}")
            return f"[오류] {section} 섹션 초안 생성에 실패했습니다: {str(e)}"
    
    def polish_text(self, text: str, tone: str = "공식적", style_guide: str = "") -> str:
        """텍스트를 윤문합니다."""
        try:
            prompt = self._create_polish_prompt(text, tone, style_guide)
            
            content = self._generate_text(prompt)
            logger.info("Hugging Face 윤문 완료")
            return content
            
        except Exception as e:
            logger.error(f"Hugging Face 윤문 실패: {e}")
            return f"[오류] 텍스트 윤문에 실패했습니다: {str(e)}"
