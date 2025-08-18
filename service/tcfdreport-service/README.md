# TCFD Report Service

TCFD(기후 관련 재무 정보 공개) 보고서 생성을 위한 서비스입니다.

## Requirements 파일

### 로컬 개발용
```bash
pip install -r requirements.txt
```
- 개발 도구 포함 (pytest, black, isort)
- 전체 기능 테스트 가능

### Railway 배포용
```bash
pip install -r requirements.prod.txt
```
- 최소한의 필수 패키지만 포함
- 빌드 시간 최적화
- 메모리 사용량 최적화

## 로컬 실행

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서비스 실행
python -m uvicorn app.main:app --host 0.0.0.0 --port 8006
```

## Railway 배포

Railway에서는 자동으로 `requirements.prod.txt`를 사용하여 배포됩니다.

## 주요 기능

- TCFD 11개 핵심 인덱스 데이터 입력
- 회사 재무정보 조회
- TCFD 프레임워크 기반 분석
- RAG 기반 보고서 생성
