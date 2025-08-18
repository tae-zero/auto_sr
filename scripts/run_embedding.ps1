# RAG 임베딩 실행 스크립트 (PowerShell)

Write-Host "🚀 RAG 임베딩 프로세스 시작" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Cyan

# 현재 디렉토리를 프로젝트 루트로 변경
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Split-Path -Parent $scriptPath)

# 가상환경 확인 (선택사항)
if (Test-Path "venv") {
    Write-Host "📦 가상환경 활성화 중..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# 필요한 패키지 설치
Write-Host "📦 임베딩 패키지 설치 중..." -ForegroundColor Yellow
pip install -r scripts/requirements.embedding.txt

# 임베딩 실행
Write-Host "🔍 임베딩 프로세스 실행 중..." -ForegroundColor Yellow
python scripts/embedding_service.py

Write-Host "✅ 임베딩 프로세스 완료!" -ForegroundColor Green
Write-Host "📁 생성된 파일:" -ForegroundColor Cyan
if (Test-Path "chroma_db") {
    Get-ChildItem "chroma_db" -Recurse | Format-Table Name, Length, LastWriteTime
}

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "🎉 RAG 임베딩 시스템 구축 완료!" -ForegroundColor Green
