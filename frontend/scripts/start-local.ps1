# 로컬 개발 환경 시작 스크립트
Write-Host "🚀 로컬 개발 환경을 시작합니다..." -ForegroundColor Green

# 환경변수 설정 (Gateway 우선 사용)
$env:NEXT_PUBLIC_GATEWAY_URL = "http://localhost:8080"
$env:NEXT_PUBLIC_AUTH_URL = "http://localhost:8008"
$env:NEXT_PUBLIC_CHATBOT_URL = "http://localhost:8006"

Write-Host "✅ 환경변수 설정 완료:" -ForegroundColor Green
Write-Host "   GATEWAY_URL: $env:NEXT_PUBLIC_GATEWAY_URL (우선 사용)" -ForegroundColor Cyan
Write-Host "   AUTH_URL: $env:NEXT_PUBLIC_AUTH_URL (백업용)" -ForegroundColor Cyan
Write-Host "   CHATBOT_URL: $env:NEXT_PUBLIC_CHATBOT_URL" -ForegroundColor Cyan

Write-Host "🔧 프론트엔드를 시작합니다..." -ForegroundColor Yellow
Write-Host "📝 이제 Gateway를 통해 API 요청이 전달됩니다!" -ForegroundColor Green
pnpm dev
