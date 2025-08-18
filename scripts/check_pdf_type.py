#!/usr/bin/env python3
"""
PDF 타입 확인 스크립트
텍스트형 PDF인지 스캔본(이미지)인지 확인
"""

import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import Dict, List

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_pdf_type(pdf_path: Path) -> Dict:
    """PDF 타입 확인"""
    try:
        doc = fitz.open(str(pdf_path))
        total_pages = len(doc)
        text_pages = 0
        image_pages = 0
        
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            
            # 텍스트 추출 시도
            text = page.get_text()
            
            if text.strip():
                text_pages += 1
            else:
                # 이미지 확인
                images = page.get_images()
                if images:
                    image_pages += 1
        
        doc.close()
        
        # 결과 분석
        text_ratio = text_pages / total_pages if total_pages > 0 else 0
        
        if text_ratio >= 0.8:
            pdf_type = "텍스트형"
        elif text_ratio >= 0.3:
            pdf_type = "혼합형"
        else:
            pdf_type = "스캔본(이미지)"
        
        return {
            "file": pdf_path.name,
            "type": pdf_type,
            "total_pages": total_pages,
            "text_pages": text_pages,
            "image_pages": image_pages,
            "text_ratio": text_ratio,
            "needs_ocr": text_ratio < 0.3
        }
        
    except Exception as e:
        logger.error(f"PDF 확인 실패: {pdf_path.name} - {e}")
        return {
            "file": pdf_path.name,
            "type": "오류",
            "error": str(e)
        }

def check_all_pdfs(base_path: str = "document") -> List[Dict]:
    """모든 PDF 파일 확인"""
    base_dir = Path(base_path)
    results = []
    
    # SR PDF 확인
    sr_dir = base_dir / "sr"
    if sr_dir.exists():
        logger.info("🔍 SR PDF 파일들 확인 중...")
        for pdf_file in sr_dir.glob("*.pdf"):
            result = check_pdf_type(pdf_file)
            results.append(result)
            logger.info(f"  {result['file']}: {result['type']} ({result.get('text_ratio', 0):.1%})")
    
    # TCFD PDF 확인
    tcfd_dir = base_dir / "tcfd"
    if tcfd_dir.exists():
        logger.info("🔍 TCFD PDF 파일들 확인 중...")
        for pdf_file in tcfd_dir.glob("*.pdf"):
            result = check_pdf_type(pdf_file)
            results.append(result)
            logger.info(f"  {result['file']}: {result['type']} ({result.get('text_ratio', 0):.1%})")
    
    return results

def print_summary(results: List[Dict]):
    """결과 요약 출력"""
    logger.info("\n📊 PDF 타입 확인 결과 요약:")
    logger.info("=" * 60)
    
    text_pdfs = [r for r in results if r.get('type') == '텍스트형']
    mixed_pdfs = [r for r in results if r.get('type') == '혼합형']
    scan_pdfs = [r for r in results if r.get('type') == '스캔본(이미지)']
    error_pdfs = [r for r in results if r.get('type') == '오류']
    
    logger.info(f"✅ 텍스트형 PDF: {len(text_pdfs)}개")
    logger.info(f"⚠️  혼합형 PDF: {len(mixed_pdfs)}개")
    logger.info(f"❌ 스캔본 PDF: {len(scan_pdfs)}개")
    logger.info(f"🚫 오류 PDF: {len(error_pdfs)}개")
    
    if scan_pdfs:
        logger.info("\n🔧 OCR이 필요한 파일들:")
        for pdf in scan_pdfs:
            logger.info(f"  - {pdf['file']}")
    
    if error_pdfs:
        logger.info("\n❌ 오류가 발생한 파일들:")
        for pdf in error_pdfs:
            logger.info(f"  - {pdf['file']}: {pdf.get('error', 'Unknown error')}")

def main():
    """메인 실행 함수"""
    logger.info("🚀 PDF 타입 확인 시작")
    
    results = check_all_pdfs()
    print_summary(results)
    
    logger.info("\n🎉 PDF 타입 확인 완료!")

if __name__ == "__main__":
    main()
