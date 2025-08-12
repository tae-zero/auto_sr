#!/bin/bash

echo "🧹 기존 의존성 정리 중..."
rm -rf node_modules
rm -rf .next
rm -rf .pnpm-store

echo "📦 pnpm 캐시 정리 중..."
pnpm store prune

echo "🔒 pnpm-lock.yaml 재생성 중..."
pnpm install --frozen-lockfile

echo "✅ 의존성 재설치 완료!"
echo "🚀 이제 도커를 다시 빌드해보세요:"
echo "   docker-compose build frontend"
echo "   docker-compose up frontend"
