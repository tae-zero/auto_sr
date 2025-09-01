# 한글 폰트 폴더

이 폴더는 TCFD 서비스에서 차트 생성 시 한글 텍스트를 표시하기 위한 폰트 파일들을 포함합니다.

## 📁 지원 폰트

### 1. NanumGothic.ttf (나눔고딕)
- **권장도**: ⭐⭐⭐⭐⭐ (가장 안정적)
- **용도**: 차트 제목, 축 레이블, 범례
- **특징**: 가독성이 좋고 범용적

### 2. NotoSansCJKkr-Regular.otf (Noto Sans CJK KR)
- **권장도**: ⭐⭐⭐⭐
- **용도**: 차트 제목, 축 레이블
- **특징**: Google에서 제공하는 고품질 폰트

### 3. malgun.ttf (맑은 고딕)
- **권장도**: ⭐⭐⭐
- **용도**: 윈도우 환경 호환성
- **특징**: 윈도우 기본 폰트

## 🚀 사용법

### 자동 폰트 감지
서비스가 시작될 때 자동으로 이 폴더의 폰트를 감지하고 사용합니다.

### 수동 폰트 추가
```python
import matplotlib.font_manager as fm

# 폰트 파일 직접 추가
font_path = "./fonts/NanumGothic.ttf"
font_prop = fm.FontProperties(fname=font_path)
fm.fontManager.addfont(font_path)
```

## 📋 폰트 우선순위

1. **NanumGothic** (가장 안정적)
2. **Noto Sans CJK KR** (Google 제공)
3. **Malgun Gothic** (윈도우 기본)
4. **NanumBarunGothic** (나눔바른고딕)
5. **NanumSquare** (나눔스퀘어)

## ⚠️ 주의사항

- 폰트 파일은 `.ttf`, `.otf` 형식을 지원합니다
- 폰트 파일명은 정확히 일치해야 합니다
- Railway 환경에서는 영어 폰트를 사용합니다 (한글 폰트 제한)

## 🔧 폰트 다운로드

### 나눔고딕
- [나눔글꼴 공식 사이트](https://hangeul.naver.com/font)
- 무료로 다운로드 가능

### Noto Sans CJK KR
- [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+KR)
- Apache 2.0 라이선스
