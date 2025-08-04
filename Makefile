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

## chat-service
build-chat:
	docker-compose build chat-service

up-chat:
	docker-compose up -d chat-service

down-chat:
	docker-compose stop chat-service

logs-chat:
	docker-compose logs -f chat-service

restart-chat:
	docker-compose stop chat-service && docker-compose up -d chat-service

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

shell-chat:
	docker-compose exec chat-service /bin/bash

shell-frontend:
	docker-compose exec frontend /bin/sh
