param(
    [string]$Service = "all",
    [switch]$NoCache,
    [switch]$Background
)

Write-Host "🐳 Docker 빌드 및 실행 스크립트" -ForegroundColor Cyan

if ($NoCache) {
    Write-Host "🧹 캐시 없이 강제 재빌드합니다..." -ForegroundColor Yellow
    if ($Service -eq "all") {
        docker-compose build --no-cache
    } else {
        docker-compose build --no-cache $Service
    }
} else {
    Write-Host "🔨 일반 빌드를 시작합니다..." -ForegroundColor Green
    if ($Service -eq "all") {
        docker-compose build
    } else {
        docker-compose build $Service
    }
}

Write-Host "🚀 서비스를 시작합니다..." -ForegroundColor Green
if ($Background) {
    if ($Service -eq "all") {
        docker-compose up -d
    } else {
        docker-compose up -d $Service
    }
    Write-Host "✅ 백그라운드에서 실행 중입니다." -ForegroundColor Green
    Write-Host "📋 로그 확인: docker-compose logs -f $Service" -ForegroundColor Cyan
} else {
    if ($Service -eq "all") {
        docker-compose up
    } else {
        docker-compose up $Service
    }
}
