@echo off
echo 🧹 기존 의존성 정리 중...
if exist node_modules rmdir /s /q node_modules
if exist .next rmdir /s /q .next
if exist .pnpm-store rmdir /s /q .pnpm-store

echo 🔒 pnpm-lock.yaml 재생성 중...
pnpm install

echo ✅ 의존성 재설치 완료!
echo 🚀 이제 도커를 다시 빌드해보세요:
echo    docker-compose build frontend
echo    docker-compose up frontend
pause
