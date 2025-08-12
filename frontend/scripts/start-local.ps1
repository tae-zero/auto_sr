# 로컬 개발 환경 시작 스크립트
Write-Host "🚀 로컬 개발 환경을 시작합니다..." -ForegroundColor Green

# 환경변수 설정
$env:NEXT_PUBLIC_AUTH_URL = "http://localhost:8008"
$env:NEXT_PUBLIC_GATEWAY_URL = "http://localhost:8080"
$env:NEXT_PUBLIC_CHATBOT_URL = "http://localhost:8006"

Write-Host "✅ 환경변수 설정 완료:" -ForegroundColor Green
Write-Host "   AUTH_URL: $env:NEXT_PUBLIC_AUTH_URL" -ForegroundColor Cyan
Write-Host "   GATEWAY_URL: $env:NEXT_PUBLIC_GATEWAY_URL" -ForegroundColor Cyan
Write-Host "   CHATBOT_URL: $env:NEXT_PUBLIC_CHATBOT_URL" -ForegroundColor Cyan

Write-Host "🔧 프론트엔드를 시작합니다..." -ForegroundColor Yellow
pnpm dev
