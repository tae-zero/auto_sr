import openai
import requests
import logging
from typing import List, Dict, Any, Optional
from ...common.config import (
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE,
    GENAI_URL, GENAI_KEY, HF_API_TOKEN, HF_MODEL
)
from ...common.schemas import ProviderEnum

logger = logging.getLogger(__name__)

class LLMService:
    """LLM (Large Language Model) 서비스"""
    
    def __init__(self):
        # OpenAI 클라이언트 설정
        if OPENAI_API_KEY:
            openai.api_key = OPENAI_API_KEY
        else:
            logger.warning("OpenAI API 키가 설정되지 않음")
    
    def generate_draft_section(self, 
                              section_name: str, 
                              question: str, 
                              context: str, 
                              style_guide: str,
                              provider: ProviderEnum) -> str:
        """
        섹션별 초안을 생성합니다.
        
        Args:
            section_name: 섹션명
            question: 질문
            context: 컨텍스트
            style_guide: 스타일 가이드
            provider: 사용할 모델 프로바이더
            
        Returns:
            str: 생성된 초안 텍스트
        """
        prompt = self._create_draft_prompt(section_name, question, context, style_guide)
        
        try:
            if provider == ProviderEnum.OPENAI:
                return self._call_openai(prompt)
            elif provider == ProviderEnum.KOALPACA:
                return self._call_koalpaca(prompt)
            elif provider == ProviderEnum.HF:
                return self._call_huggingface(prompt)
            else:
                raise ValueError(f"지원하지 않는 프로바이더: {provider}")
                
        except Exception as e:
            logger.error(f"초안 생성 실패 (프로바이더: {provider}): {e}")
            raise
    
    def polish_text(self, 
                   text: str, 
                   tone: str, 
                   style_guide: str,
                   provider: ProviderEnum) -> str:
        """
        텍스트를 윤문합니다.
        
        Args:
            text: 윤문할 텍스트
            tone: 문체 톤
            style_guide: 스타일 가이드
            provider: 사용할 모델 프로바이더
            
        Returns:
            str: 정제된 텍스트
        """
        prompt = self._create_polish_prompt(text, tone, style_guide)
        
        try:
            if provider == ProviderEnum.OPENAI:
                return self._call_openai(prompt)
            elif provider == ProviderEnum.KOALPACA:
                return self._call_koalpaca(prompt)
            elif provider == ProviderEnum.HF:
                return self._call_huggingface(prompt)
            else:
                raise ValueError(f"지원하지 않는 프로바이더: {provider}")
                
        except Exception as e:
            logger.error(f"윤문 실패 (프로바이더: {provider}): {e}")
            raise
    
    def _create_draft_prompt(self, section_name: str, question: str, context: str, style_guide: str) -> str:
        """초안 생성 프롬프트를 생성합니다."""
        return f"""다음 '근거'를 바탕으로 ESG 보고서의 섹션 초안을 작성하세요.
- [중요] 근거 문장을 인용할 때는 [1], [2]처럼 번호로 표시
- 두괄식 요약 → 핵심 bullet 3~5개 → 상세 설명 순서
- ESG/회계 전문 용어, 수치, 기간을 정확히 유지
- 외부 사실 추정/창작 금지, 근거 없는 수치 생성 금지
- 문체: 공식적·객관적, 존칭/구어체 금지

[섹션]
{section_name}

[질문]
{question}

[근거]
{context}

[초안 작성]"""

    def _create_polish_prompt(self, text: str, tone: str, style_guide: str) -> str:
        """윤문 프롬프트를 생성합니다."""
        return f"""아래 텍스트를 윤문하세요.
- 용어/서식 일관화(ESG/회계 기준)
- 중복/군더더기 제거, 문장 간 논리 연결 강화
- 숫자/단위/연도 표기 통일
- 어조: {tone}

[스타일 가이드]
{style_guide}

[원문]
{text}

[윤문 결과]"""

    def _call_openai(self, prompt: str) -> str:
        """OpenAI API를 호출합니다."""
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API 키가 설정되지 않음")
        
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "당신은 ESG 보고서 작성 전문가입니다. 정확하고 전문적인 내용을 생성해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=OPENAI_MAX_TOKENS,
                temperature=OPENAI_TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API 호출 실패: {e}")
            raise
    
    def _call_koalpaca(self, prompt: str) -> str:
        """KoAlpaca API를 호출합니다."""
        if not GENAI_URL:
            raise ValueError("KoAlpaca API URL이 설정되지 않음")
        
        try:
            headers = {"Content-Type": "application/json"}
            if GENAI_KEY:
                headers["Authorization"] = f"Bearer {GENAI_KEY}"
            
            payload = {
                "model": "koalpaca-3.8b",
                "messages": [
                    {"role": "system", "content": "당신은 ESG 보고서 작성 전문가입니다. 정확하고 전문적인 내용을 생성해주세요."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            response = requests.post(
                GENAI_URL,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            logger.error(f"KoAlpaca API 호출 실패: {e}")
            raise
    
    def _call_huggingface(self, prompt: str) -> str:
        """Hugging Face Inference API를 호출합니다."""
        if not HF_API_TOKEN:
            raise ValueError("Hugging Face API 토큰이 설정되지 않음")
        
        try:
            headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 2000,
                    "temperature": 0.3,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{HF_MODEL}",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").replace(prompt, "").strip()
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Hugging Face API 호출 실패: {e}")
            raise
