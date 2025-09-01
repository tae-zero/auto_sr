import requests
import logging
import torch
import os
from typing import Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
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
        self.model = None
        self.tokenizer = None
        self.pipeline = None
        
        if self.use_local_model:
            # 로컬 모델 로딩
            self._load_local_model()
        else:
            # Hugging Face Hub에서 직접 모델 로딩
            self._load_hf_hub_model()
    
    def _load_hf_hub_model(self):
        """Hugging Face Hub에서 모델을 직접 로딩합니다."""
        try:
            logger.info("Hugging Face Hub에서 모델 로딩 시작")
            
            # 환경변수에서 토큰 가져오기
            hf_token = os.getenv("HF_TOKEN")
            if not hf_token:
                logger.warning("HF_TOKEN이 설정되지 않음")
                return
            
            # 모델 리포지토리 설정
            model_repo = HF_MODEL or "jeongtaeyeong/tcfd-polyglot-3.8b-merged"
            logger.info(f"모델 리포지토리: {model_repo}")
            
            # GPU 사용 가능 여부 확인
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"사용 디바이스: {device}")
            
            # 토크나이저 로드 (Fast/Slow 폴백 전략)
            try:
                # 1차: Fast 토크나이저 시도
                logger.info("Fast 토크나이저 로딩 시도")
                self.tokenizer = AutoTokenizer.from_pretrained(
                    model_repo, 
                    use_auth_token=hf_token,
                    trust_remote_code=True,
                    use_fast=True,
                    force_download=True
                )
                logger.info("Fast 토크나이저 로딩 성공")
            except Exception as e_fast:
                logger.warning(f"Fast 토크나이저 로딩 실패: {e_fast}")
                try:
                    # 2차: Slow 토크나이저로 폴백 (SentencePiece 기반)
                    logger.info("Slow 토크나이저로 폴백 시도")
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        model_repo, 
                        use_auth_token=hf_token,
                        trust_remote_code=True,
                        use_fast=False,  # ← 중요한 부분
                        force_download=True
                    )
                    logger.info("Slow 토크나이저 로딩 성공")
                except Exception as e_slow:
                    logger.error(f"Slow 토크나이저도 실패: {e_slow}")
                    # 3차: 베이스 모델 토크나이저로 최후 폴백
                    logger.warning("베이스 모델 토크나이저로 최후 폴백")
                    self.tokenizer = AutoTokenizer.from_pretrained(
                        "EleutherAI/polyglot-ko-3.8b",
                        use_auth_token=hf_token,
                        use_fast=False
                    )
                    logger.info("베이스 모델 토크나이저 로딩 성공")
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # 모델 로드 (CPU 환경 고려)
            if device == "cpu":
                # CPU 환경에서는 float32 사용 (float16은 CPU에서 지원되지 않음)
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_repo,
                    torch_dtype=torch.float32,  # CPU에서는 float32 사용
                    use_auth_token=hf_token,
                    trust_remote_code=True,
                    low_cpu_mem_usage=True,
                    force_download=True
                ).to("cpu")
                logger.info("CPU 환경에서 float32로 모델 로딩")
            else:
                # GPU 환경에서는 float16 사용
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_repo,
                    torch_dtype=torch.float16,
                    use_auth_token=hf_token,
                    trust_remote_code=True,
                    device_map="auto",
                    force_download=True
                )
                logger.info("GPU 환경에서 float16으로 모델 로딩")
            
            # 파이프라인 생성
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,
                max_new_tokens=1000,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )
            
            logger.info("Hugging Face Hub 모델 로딩 완료")
            
        except Exception as e:
            logger.exception("Hugging Face Hub 모델 로딩 실패")
            logger.info("API 호출 방식으로 fallback")
            self.use_local_model = False
    
    def _load_local_model(self):
        """로컬 모델을 로드합니다. (기존 방식 보존)"""
        try:
            logger.info(f"로컬 모델 로딩 시작: {HF_LOCAL_MODEL_PATH}")
            
            # GPU 사용 가능 여부 확인
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"사용 디바이스: {device}")
            
            # 토크나이저 로드
            self.tokenizer = AutoTokenizer.from_pretrained(
                HF_LOCAL_MODEL_PATH,
                trust_remote_code=True
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # 모델 로드 (메모리 최적화)
            self.model = AutoModelForCausalLM.from_pretrained(
                HF_LOCAL_MODEL_PATH,
                torch_dtype=torch.float16,
                device_map="auto" if device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # 파이프라인 생성
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if device == "cuda" else -1,
                max_new_tokens=1000,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )
            
            logger.info("로컬 모델 로딩 완료")
            
        except Exception as e:
            logger.error(f"로컬 모델 로딩 실패: {e}")
            logger.info("API 호출 방식으로 fallback")
            self.use_local_model = False
    
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
        """로딩된 모델로 텍스트를 생성합니다."""
        try:
            if not self.pipeline:
                logger.error("모델이 로드되지 않음")
                return "[오류] 모델이 로드되지 않았습니다."
            
            # 프롬프트 전처리
            formatted_prompt = self._format_prompt_for_model(prompt)
            
            # 텍스트 생성
            result = self.pipeline(
                formatted_prompt,
                max_new_tokens=1000,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1
            )
            
            if result and len(result) > 0:
                generated_text = result[0]['generated_text']
                # 프롬프트 부분 제거하고 생성된 텍스트만 반환
                if formatted_prompt in generated_text:
                    generated_text = generated_text.replace(formatted_prompt, '').strip()
                return generated_text
            else:
                return "[오류] 텍스트 생성에 실패했습니다."
                
        except Exception as e:
            logger.error(f"모델 텍스트 생성 실패: {e}")
            return f"[오류] 모델 텍스트 생성에 실패했습니다: {str(e)}"
    
    def _format_prompt_for_model(self, prompt: str) -> str:
        """모델용 프롬프트를 포맷팅합니다."""
        # TCFD 전문가 프롬프트 추가
        system_prompt = "당신은 TCFD 기후 관련 재무정보 공시 보고서 작성 전문가입니다. 전문적이고 체계적인 보고서를 작성해주세요."
        return f"{system_prompt}\n\n{prompt}"
    
    def _generate_text(self, prompt: str) -> str:
        """텍스트 생성 방식에 따라 적절한 메서드를 호출합니다."""
        if self.pipeline:
            return self._generate_with_loaded_model(prompt)
        else:
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
