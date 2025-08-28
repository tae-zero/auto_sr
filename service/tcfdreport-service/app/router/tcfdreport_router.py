from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Dict, Any
import logging
import asyncpg
import os
from datetime import datetime
import tempfile
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

logger = logging.getLogger(__name__)

tcfdreport_router = APIRouter()

def _return_html_fallback(html_content: str, data: Dict[str, Any], error_type: str):
    """HTML fallback 반환 헬퍼 메서드"""
    try:
        import tempfile
        
        # 임시 HTML 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as tmp_file:
            tmp_file.write(html_content)
            tmp_file_path = tmp_file.name
        
        # 파일명 생성 (오류 타입 포함)
        filename = f"{data.get('company_name', 'TCFD')}_보고서_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{error_type}.html"
        
        logger.info(f"HTML fallback 반환: {filename}")
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type="text/html"
        )
    except Exception as e:
        logger.error(f"HTML fallback 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"HTML fallback 생성 실패: {str(e)}")

# 데이터베이스 연결 함수
async def get_db_connection():
    """데이터베이스 연결 반환"""
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise Exception("DATABASE_URL 환경변수가 설정되지 않았습니다")
        
        # URL 스키마 수정
        if database_url.startswith("postgresql+asyncpg://"):
            database_url = "postgresql://" + database_url[len("postgresql+asyncpg://"):]
        elif database_url.startswith("postgres://"):
            database_url = "postgresql://" + database_url[len("postgres://"):]
        
        conn = await asyncpg.connect(database_url)
        return conn
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {str(e)}")
        raise

@tcfdreport_router.get("/")
async def root():
    return {"message": "TCFD Report Service"}

@tcfdreport_router.get("/health")
async def health_check():
    return {"status": "healthy"}

@tcfdreport_router.post("/inputs")
async def create_tcfd_inputs(data: Dict[str, Any]):
    """TCFD 입력 데이터 생성"""
    conn = None
    try:
        logger.info(f"TCFD 입력 데이터 생성 요청: {data}")
        
        # 필수 필드 검증
        if not data.get('company_name'):
            raise HTTPException(status_code=400, detail="회사명은 필수입니다")
        if not data.get('user_id'):
            raise HTTPException(status_code=400, detail="사용자 ID는 필수입니다")
        
        # 데이터베이스 연결
        conn = await get_db_connection()
        
        # 입력된 필드만 추출하여 저장
        fields_to_insert = ['company_name', 'user_id']
        values_to_insert = [data['company_name'], data['user_id']]
        
        # 선택적 필드들 (입력된 경우에만 저장)
        optional_fields = [
            'governance_g1', 'governance_g2',
            'strategy_s1', 'strategy_s2', 'strategy_s3',
            'risk_management_r1', 'risk_management_r2', 'risk_management_r3',
            'metrics_targets_m1', 'metrics_targets_m2', 'metrics_targets_m3'
        ]
        
        for field in optional_fields:
            if data.get(field) and data[field].strip():  # 빈 문자열이 아닌 경우에만
                fields_to_insert.append(field)
                values_to_insert.append(data[field])
        
        # SQL 쿼리 생성
        placeholders = ', '.join([f'${i+1}' for i in range(len(values_to_insert))])
        fields_str = ', '.join(fields_to_insert)
        
        query = f"""
            INSERT INTO tcfd_inputs ({fields_str}, created_at, updated_at)
            VALUES ({placeholders}, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, company_name, created_at
        """
        
        # 데이터 저장
        result = await conn.fetchrow(query, *values_to_insert)
        
        logger.info(f"TCFD 입력 데이터 저장 성공: ID={result['id']}, 회사={result['company_name']}")
        
        return {
            "success": True,
            "message": "TCFD 입력 데이터가 성공적으로 저장되었습니다",
            "data": {
                "id": result['id'],
                "company_name": result['company_name'],
                "user_id": data['user_id'],
                "created_at": result['created_at'].isoformat(),
                "saved_fields": fields_to_insert
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TCFD 입력 데이터 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"데이터 저장 실패: {str(e)}")
    finally:
        if conn:
            await conn.close()

@tcfdreport_router.get("/inputs/{company_name}")
async def get_tcfd_inputs(company_name: str):
    """회사별 TCFD 입력 데이터 조회"""
    conn = None
    try:
        logger.info(f"TCFD 입력 데이터 조회 요청: {company_name}")
        
        # 데이터베이스 연결
        conn = await get_db_connection()
        
        # 최신 데이터 조회
        query = """
            SELECT * FROM tcfd_inputs 
            WHERE company_name = $1 
            ORDER BY created_at DESC 
            LIMIT 1
        """
        
        result = await conn.fetchrow(query, company_name)
        
        if not result:
            return {
                "success": True,
                "company_name": company_name,
                "message": "해당 회사의 TCFD 데이터가 없습니다",
                "data": {
                    "governance_g1": "",
                    "governance_g2": "",
                    "strategy_s1": "",
                    "strategy_s2": "",
                    "strategy_s3": "",
                    "risk_management_r1": "",
                    "risk_management_r2": "",
                    "risk_management_r3": "",
                    "metrics_targets_m1": "",
                    "metrics_targets_m2": "",
                    "metrics_targets_m3": ""
                }
            }
        
        # 데이터베이스 결과를 딕셔너리로 변환
        data = {
            "governance_g1": result.get('governance_g1', ''),
            "governance_g2": result.get('governance_g2', ''),
            "strategy_s1": result.get('strategy_s1', ''),
            "strategy_s2": result.get('strategy_s2', ''),
            "strategy_s3": result.get('strategy_s3', ''),
            "risk_management_r1": result.get('risk_management_r1', ''),
            "risk_management_r2": result.get('risk_management_r2', ''),
            "risk_management_r3": result.get('risk_management_r3', ''),
            "metrics_targets_m1": result.get('metrics_targets_m1', ''),
            "metrics_targets_m2": result.get('metrics_targets_m2', ''),
            "metrics_targets_m3": result.get('metrics_targets_m3', '')
        }
        
        logger.info(f"TCFD 입력 데이터 조회 성공: 회사={company_name}")
        
        return {
            "success": True,
            "company_name": company_name,
            "data": data,
            "metadata": {
                "id": result['id'],
                "user_id": result.get('user_id'),
                "created_at": result['created_at'].isoformat(),
                "updated_at": result['updated_at'].isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"TCFD 입력 데이터 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
    finally:
        if conn:
            await conn.close()

@tcfdreport_router.post("/download/word")
async def download_tcfd_report_as_word(data: Dict[str, Any]):
    """TCFD 보고서를 Word 문서로 다운로드"""
    try:
        logger.info(f"Word 문서 다운로드 요청: {data.get('company_name', 'Unknown')}")
        
        # 필수 필드 검증
        if not data.get('draft') or not data.get('polished'):
            raise HTTPException(status_code=400, detail="초안과 윤문 내용이 필요합니다")
        
        # 회사명 추출 (draft 내용에서 추출)
        company_name = "TCFD"
        if data.get('draft'):
            # draft 내용에서 회사명 추출 시도
            draft_content = data['draft']
            if '**회사명**:' in draft_content:
                company_name = draft_content.split('**회사명**:')[1].split('\n')[0].strip()
            elif '회사명:' in draft_content:
                company_name = draft_content.split('회사명:')[1].split('\n')[0].strip()
        
        # Word 문서 생성
        doc = Document()
        
        # 제목
        title = doc.add_heading(f"{company_name} TCFD 보고서", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 회사명
        company_para = doc.add_paragraph(f"회사: {company_name}")
        company_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 생성일시
        timestamp_para = doc.add_paragraph(f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}")
        timestamp_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 초안 섹션
        doc.add_heading("📝 초안 생성", level=1)
        doc.add_paragraph(data['draft'])
        
        # 윤문 섹션
        doc.add_heading("✨ 윤문된 텍스트", level=1)
        doc.add_paragraph(data['polished'])
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            doc.save(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # 파일명 생성
        filename = f"{company_name}_보고서_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        logger.error(f"Word 문서 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Word 문서 생성 실패: {str(e)}")

@tcfdreport_router.post("/download/pdf")
async def download_tcfd_report_as_pdf(data: Dict[str, Any]):
    """TCFD 보고서를 PDF로 다운로드"""
    try:
        logger.info(f"PDF 다운로드 요청: {data.get('company_name', 'Unknown')}")
        
        # 필수 필드 검증
        if not data.get('draft') or not data.get('polished'):
            raise HTTPException(status_code=400, detail="초안과 윤문 내용이 필요합니다")
        
        # 회사명 추출 (draft 내용에서 추출)
        company_name = "TCFD"
        if data.get('draft'):
            # draft 내용에서 회사명 추출 시도
            draft_content = data['draft']
            if '**회사명**:' in draft_content:
                company_name = draft_content.split('**회사명**:')[1].split('\n')[0].strip()
            elif '회사명:' in draft_content:
                company_name = draft_content.split('회사명:')[1].split('\n')[0].strip()
        
        # PDF 생성을 위한 HTML 생성 (간단한 버전)
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{company_name} TCFD 보고서</title>
            <style>
                body {{ font-family: 'Malgun Gothic', Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ text-align: center; color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }}
                h2 {{ color: #059669; margin-top: 30px; }}
                .company-info {{ text-align: center; color: #6b7280; margin: 20px 0; }}
                .content {{ background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .timestamp {{ text-align: center; color: #9ca3af; font-size: 14px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>{company_name} TCFD 보고서</h1>
            <div class="company-info">회사: {company_name}</div>
            <div class="timestamp">생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</div>
            
            <h2>📝 초안 생성</h2>
            <div class="content">{data['draft'].replace(chr(10), '<br>')}</div>
            
            <h2>✨ 윤문된 텍스트</h2>
            <div class="content">{data['polished'].replace(chr(10), '<br>')}</div>
        </body>
        </html>
        """
        
        # HTML을 PDF로 변환
        try:
            from weasyprint import HTML
            import tempfile
            
            # 임시 HTML 파일 생성
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as tmp_html:
                tmp_html.write(html_content)
                tmp_html_path = tmp_html.name
            
            # PDF 파일 경로
            pdf_path = tmp_html_path.replace('.html', '.pdf')
            
            # HTML을 PDF로 변환
            HTML(filename=tmp_html_path).write_pdf(pdf_path)
            
            # 임시 HTML 파일 삭제
            import os
            os.unlink(tmp_html_path)
            
            # 파일명 생성
            filename = f"{company_name}_보고서_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            logger.info(f"✅ PDF 생성 성공: {filename}")
            return FileResponse(
                path=pdf_path,
                filename=filename,
                media_type="application/pdf"
            )
            
        except ImportError as import_error:
            # weasyprint가 없는 경우 HTML을 그대로 반환
            logger.warning(f"weasyprint가 설치되지 않아 HTML을 반환합니다: {import_error}")
            return _return_html_fallback(html_content, data, "weasyprint_import_error")
            
        except Exception as weasyprint_error:
            # WeasyPrint 실행 중 오류 (시스템 라이브러리 문제 등)
            logger.warning(f"WeasyPrint 실행 오류로 HTML을 반환합니다: {weasyprint_error}")
            return _return_html_fallback(html_content, data, "weasyprint_runtime_error")
        
    except Exception as e:
        logger.error(f"PDF 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF 생성 실패: {str(e)}")

@tcfdreport_router.post("/download/combined")
async def download_tcfd_report_combined(data: Dict[str, Any]):
    """TCFD 보고서를 Word와 PDF 모두 다운로드 (ZIP 파일)"""
    try:
        logger.info(f"통합 다운로드 요청: {data.get('company_name', 'Unknown')}")
        
        # 필수 필드 검증
        if not data.get('draft') or not data.get('polished'):
            raise HTTPException(status_code=400, detail="초안과 윤문 내용이 필요합니다")
        
        # Word 문서 생성
        doc = Document()
        
        # 제목
        title = doc.add_heading(f"{data.get('company_name', '회사')} TCFD 보고서", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 회사명
        if data.get('company_name'):
            company_para = doc.add_paragraph(f"회사: {data['company_name']}")
            company_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 생성일시
        timestamp_para = doc.add_paragraph(f"생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}")
        timestamp_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 초안 섹션
        doc.add_heading("📝 초안 생성", level=1)
        doc.add_paragraph(data['draft'])
        
        # 윤문 섹션
        doc.add_heading("✨ 윤문된 텍스트", level=1)
        doc.add_paragraph(data['polished'])
        
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
            doc.save(tmp_file.name)
            tmp_file_path = tmp_file.name
        
        # 파일명 생성
        filename = f"{data.get('company_name', 'TCFD')}_보고서_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
        
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        
    except Exception as e:
        logger.error(f"통합 다운로드 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"통합 다운로드 실패: {str(e)}")