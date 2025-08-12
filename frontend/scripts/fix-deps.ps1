Write-Host "🧹 기존 의존성 정리 중..." -ForegroundColor Green

if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules"
    Write-Host "node_modules 삭제 완료" -ForegroundColor Yellow
}

if (Test-Path ".next") {
    Remove-Item -Recurse -Force ".next"
    Write-Host ".next 삭제 완료" -ForegroundColor Yellow
}

if (Test-Path ".pnpm-store") {
    Remove-Item -Recurse -Force ".pnpm-store"
    Write-Host ".pnpm-store 삭제 완료" -ForegroundColor Yellow
}

Write-Host "🔒 pnpm-lock.yaml 재생성 중..." -ForegroundColor Green
pnpm install

Write-Host "✅ 의존성 재설치 완료!" -ForegroundColor Green
Write-Host "🚀 이제 도커를 다시 빌드해보세요:" -ForegroundColor Cyan
Write-Host "   docker-compose build frontend" -ForegroundColor White
Write-Host "   docker-compose up frontend" -ForegroundColor White

Read-Host "계속하려면 Enter를 누르세요"
