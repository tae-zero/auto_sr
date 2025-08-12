# 모든 명령어 앞에 'make' 를 붙여서 실행해야 함

# 🔧 공통 명령어
up:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose down && docker-compose up -d --build

ps:
	docker-compose ps

# 🚀 마이크로서비스별 명령어

## frontend
build-frontend:
	docker-compose build frontend

up-frontend:
	docker-compose up -d frontend

down-frontend:
	docker-compose stop frontend

logs-frontend:
	docker-compose logs -f frontend

restart-frontend:
	docker-compose stop frontend && docker-compose up -d frontend

## gateway
build-gateway:
	docker-compose build gateway

up-gateway:
	docker-compose up -d gateway

down-gateway:
	docker-compose stop gateway

logs-gateway:
	docker-compose logs -f gateway

restart-gateway:
	docker-compose stop gateway && docker-compose up -d gateway

## chatbot-service
build-chatbot:
	docker-compose build chatbot-service

up-chatbot:
	docker-compose up -d chatbot-service

down-chatbot:
	docker-compose stop chatbot-service

logs-chatbot:
	docker-compose logs -f chatbot-service

restart-chatbot:
	docker-compose stop chatbot-service && docker-compose up -d chatbot-service

## redis
up-redis:
	docker-compose up -d redis

down-redis:
	docker-compose stop redis

logs-redis:
	docker-compose logs -f redis

restart-redis:
	docker-compose stop redis && docker-compose up -d redis

# 🧹 유틸리티 명령어
clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

clean-all:
	docker-compose down -v --remove-orphans
	docker system prune -af
	docker volume prune -f

# 📊 상태 확인
status:
	docker-compose ps
	docker-compose top

# 🔍 디버깅
shell-gateway:
	docker-compose exec gateway /bin/bash

shell-chatbot:
	docker-compose exec chatbot-service /bin/bash

shell-frontend:
	docker-compose exec frontend /bin/sh

# 🚀 CI/CD 관련 명령어
ci-status:
	@echo "🔍 CI/CD 상태 확인 중..."
	@./scripts/deploy-status.sh

ci-deploy:
	@echo "🚀 CI/CD 배포 트리거..."
	@echo "코드를 main 또는 develop 브랜치에 푸시하세요:"
	@echo "git push origin main"
	@echo "또는"
	@echo "git push origin develop"
	@echo ""
	@echo "🚂 Railway 배포는 수동으로 설정해야 합니다:"
	@echo "각 서비스를 별도 프로젝트로 배포하세요."
	@echo "자세한 내용은 RAILWAY-DEPLOYMENT.md를 참조하세요."

ci-logs:
	@echo "📊 GitHub Actions 로그 확인:"
	@echo "https://github.com/$(shell git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\).*/\1/')/actions"

ci-secrets:
	@echo "🔐 필요한 GitHub Secrets:"
	@echo "VERCEL_TOKEN: Vercel API 토큰"
	@echo "VERCEL_ORG_ID: Vercel 조직 ID"
	@echo "VERCEL_PROJECT_ID: Vercel 프로젝트 ID"
	@echo "RAILWAY_TOKEN: Railway API 토큰"

# 🧪 테스트 관련 명령어
test-services:
	@echo "🧪 서비스 테스트 실행 중..."
	@./scripts/test-services.sh

test-local:
	@echo "🧪 로컬 환경 테스트..."
	@make up
	@sleep 30
	@./scripts/test-services.sh
	@make down
