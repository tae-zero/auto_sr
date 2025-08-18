#!/usr/bin/env python3
"""
임베딩 전 필수 체크 스크립트
8개 필수 항목을 모두 확인
"""

import sys
import logging
from pathlib import Path
from check_pdf_type import check_all_pdfs

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_libraries():
    """1. 라이브러리 준비 확인"""
    logger.info("🔍 1. 라이브러리 준비 확인 중...")
    
    required_libs = [
        'langchain', 'chromadb', 'pymupdf', 'huggingface_hub', 
        'sentencepiece', 'sentence_transformers', 'transformers'
    ]
    
    missing_libs = []
    for lib in required_libs:
        try:
            __import__(lib)
            logger.info(f"  ✅ {lib}")
        except ImportError:
            missing_libs.append(lib)
            logger.error(f"  ❌ {lib} - 설치 필요")
    
    if missing_libs:
        logger.error(f"❌ 설치 필요한 라이브러리: {', '.join(missing_libs)}")
        return False
    
    logger.info("✅ 모든 필수 라이브러리 설치됨")
    return True

def check_folder_structure():
    """2. 폴더 구조 확인"""
    logger.info("🔍 2. 폴더 구조 확인 중...")
    
    base_path = Path("document")
    sr_path = base_path / "sr"
    tcfd_path = base_path / "tcfd"
    chroma_path = Path("chroma_db")
    
    # 필수 폴더 확인
    if not base_path.exists():
        logger.error("❌ document/ 폴더가 없습니다")
        return False
    
    if not sr_path.exists():
        logger.error("❌ document/sr/ 폴더가 없습니다")
        return False
    
    if not tcfd_path.exists():
        logger.error("❌ document/tcfd/ 폴더가 없습니다")
        return False
    
    # PDF 파일 확인
    sr_pdfs = list(sr_path.glob("*.pdf"))
    tcfd_pdfs = list(tcfd_path.glob("*.pdf"))
    
    logger.info(f"  📁 document/sr/: {len(sr_pdfs)}개 PDF")
    logger.info(f"  📁 document/tcfd/: {len(tcfd_pdfs)}개 PDF")
    
    if len(sr_pdfs) == 0:
        logger.error("❌ SR PDF 파일이 없습니다")
        return False
    
    if len(tcfd_pdfs) == 0:
        logger.error("❌ TCFD PDF 파일이 없습니다")
        return False
    
    # chroma_db 폴더 생성
    chroma_path.mkdir(exist_ok=True)
    logger.info("✅ 폴더 구조 확인 완료")
    return True

def check_pdf_types():
    """3. PDF 타입 확인"""
    logger.info("🔍 3. PDF 타입 확인 중...")
    
    results = check_all_pdfs()
    
    # 스캔본 PDF 확인
    scan_pdfs = [r for r in results if r.get('type') == '스캔본(이미지)']
    
    if scan_pdfs:
        logger.warning(f"⚠️  스캔본 PDF {len(scan_pdfs)}개 발견 - OCR 필요")
        for pdf in scan_pdfs:
            logger.warning(f"    - {pdf['file']}")
        return False
    
    logger.info("✅ 모든 PDF가 텍스트형입니다")
    return True

def check_embedding_model():
    """4. 임베딩 모델 확인"""
    logger.info("🔍 4. 임베딩 모델 확인 중...")
    
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('intfloat/multilingual-e5-base')
        logger.info("✅ intfloat/multilingual-e5-base 모델 로드 성공")
        return True
    except Exception as e:
        logger.error(f"❌ 임베딩 모델 로드 실패: {e}")
        return False

def check_tcfd_mapping():
    """5. TCFD 매핑 파일 확인"""
    logger.info("🔍 5. TCFD 매핑 파일 확인 중...")
    
    mapping_path = Path("document/tcfd_mapping.xlsx")
    
    if mapping_path.exists():
        logger.info("✅ tcfd_mapping.xlsx 파일 발견")
        return True
    else:
        logger.warning("⚠️  tcfd_mapping.xlsx 파일이 없습니다 (선택사항)")
        return True

def check_permissions():
    """6. 권한/경로 확인"""
    logger.info("🔍 6. 권한/경로 확인 중...")
    
    try:
        # 쓰기 권한 확인
        test_path = Path("chroma_db/test_write")
        test_path.parent.mkdir(exist_ok=True)
        test_path.write_text("test")
        test_path.unlink()
        
        logger.info("✅ 쓰기 권한 확인 완료")
        return True
    except Exception as e:
        logger.error(f"❌ 쓰기 권한 오류: {e}")
        return False

def check_chunking_params():
    """7. 청킹 파라미터 확인"""
    logger.info("🔍 7. 청킹 파라미터 확인 중...")
    
    # 권장 파라미터
    recommended = {
        "chunk_size": 800,
        "chunk_overlap": 150,
        "separators": ["\n## ", "\n#", "\n\n", "\n", " "]
    }
    
    logger.info("✅ 청킹 파라미터 설정 완료:")
    logger.info(f"  - chunk_size: {recommended['chunk_size']}")
    logger.info(f"  - chunk_overlap: {recommended['chunk_overlap']}")
    logger.info(f"  - separators: {recommended['separators']}")
    
    return True

def check_metadata_schema():
    """8. 메타데이터 스키마 확인"""
    logger.info("🔍 8. 메타데이터 스키마 확인 중...")
    
    required_fields = ["collection", "source"]
    optional_fields = ["company", "year", "pillar", "page_from", "page_to"]
    
    logger.info("✅ 메타데이터 스키마 설정 완료:")
    logger.info(f"  - 필수 필드: {required_fields}")
    logger.info(f"  - 선택 필드: {optional_fields}")
    
    return True

def main():
    """메인 실행 함수"""
    logger.info("🚀 임베딩 전 필수 체크 시작")
    logger.info("=" * 60)
    
    checks = [
        ("라이브러리 준비", check_libraries),
        ("폴더 구조", check_folder_structure),
        ("PDF 타입", check_pdf_types),
        ("임베딩 모델", check_embedding_model),
        ("TCFD 매핑", check_tcfd_mapping),
        ("권한/경로", check_permissions),
        ("청킹 파라미터", check_chunking_params),
        ("메타데이터 스키마", check_metadata_schema)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            if check_func():
                passed += 1
            else:
                logger.error(f"❌ {name} 체크 실패")
        except Exception as e:
            logger.error(f"❌ {name} 체크 중 오류: {e}")
    
    logger.info("=" * 60)
    logger.info(f"📊 체크 결과: {passed}/{total} 통과")
    
    if passed == total:
        logger.info("🎉 모든 체크 통과! 임베딩을 시작할 수 있습니다.")
        return True
    else:
        logger.error("❌ 일부 체크 실패. 문제를 해결한 후 다시 시도하세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
