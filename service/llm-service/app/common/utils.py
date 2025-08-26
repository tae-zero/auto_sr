import logging
import uuid
import time
from typing import Dict, Any, Optional
from functools import wraps
from pathlib import Path
import shutil
import asyncio

logger = logging.getLogger(__name__)

def generate_request_id() -> str:
    """고유한 요청 ID를 생성합니다."""
    return str(uuid.uuid4())

def log_request_info(request_id: str, endpoint: str, **kwargs):
    """요청 정보를 로깅합니다."""
    logger.info(f"[{request_id}] {endpoint} 호출 - {kwargs}")

def log_response_info(request_id: str, endpoint: str, response_time: float, **kwargs):
    """응답 정보를 로깅합니다."""
    logger.info(f"[{request_id}] {endpoint} 완료 - {response_time:.2f}초 - {kwargs}")

def timing_decorator(func):
    """함수 실행 시간을 측정하는 데코레이터"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} 실행 시간: {execution_time:.2f}초")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 실행 실패 ({execution_time:.2f}초): {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} 실행 시간: {execution_time:.2f}초")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 실행 실패 ({execution_time:.2f}초): {e}")
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

def ensure_directory_exists(directory_path: str) -> bool:
    """디렉토리가 존재하는지 확인하고, 없으면 생성합니다."""
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"디렉토리 생성 실패 {directory_path}: {e}")
        return False

def safe_file_operation(operation_func):
    """파일 작업을 안전하게 수행하는 데코레이터"""
    @wraps(operation_func)
    def wrapper(*args, **kwargs):
        try:
            return operation_func(*args, **kwargs)
        except FileNotFoundError as e:
            logger.error(f"파일을 찾을 수 없음: {e}")
            raise
        except PermissionError as e:
            logger.error(f"파일 접근 권한 없음: {e}")
            raise
        except Exception as e:
            logger.error(f"파일 작업 실패: {e}")
            raise
    return wrapper

@safe_file_operation
def backup_file(file_path: str, backup_suffix: str = ".backup") -> str:
    """파일을 백업합니다."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"백업할 파일이 존재하지 않음: {file_path}")
    
    backup_path = str(path) + backup_suffix
    shutil.copy2(file_path, backup_path)
    logger.info(f"파일 백업 완료: {file_path} -> {backup_path}")
    return backup_path

@safe_file_operation
def safe_file_rename(old_path: str, new_path: str) -> bool:
    """파일을 안전하게 이름 변경합니다."""
    old_file = Path(old_path)
    new_file = Path(new_path)
    
    if not old_file.exists():
        raise FileNotFoundError(f"이름 변경할 파일이 존재하지 않음: {old_path}")
    
    # 새 경로에 파일이 있으면 백업
    if new_file.exists():
        backup_file(str(new_file))
    
    old_file.rename(new_file)
    logger.info(f"파일 이름 변경 완료: {old_path} -> {new_path}")
    return True

def validate_file_size(file_path: str, max_size: int) -> bool:
    """파일 크기를 검증합니다."""
    try:
        file_size = Path(file_path).stat().st_size
        if file_size > max_size:
            logger.warning(f"파일 크기 초과: {file_path} ({file_size} > {max_size})")
            return False
        return True
    except Exception as e:
        logger.error(f"파일 크기 검증 실패: {e}")
        return False

def format_file_size(size_bytes: int) -> str:
    """바이트 크기를 사람이 읽기 쉬운 형태로 변환합니다."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def truncate_text(text: str, max_length: int = 1000) -> str:
    """텍스트를 최대 길이로 자릅니다."""
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length].rsplit(' ', 1)[0]
    return truncated + "..."

def sanitize_filename(filename: str) -> str:
    """파일명을 안전하게 만듭니다."""
    # 위험한 문자들을 제거하거나 대체
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    sanitized = filename
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    return sanitized[:255]  # 파일명 길이 제한
