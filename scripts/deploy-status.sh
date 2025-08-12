#!/bin/bash

# 🚀 배포 상태 확인 스크립트
# 이 스크립트는 CI/CD 파이프라인의 상태를 확인합니다.

set -e

echo "🔍 CI/CD 배포 상태 확인 중..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# GitHub Actions 상태 확인
check_github_actions() {
    echo -e "\n${BLUE}📊 GitHub Actions 상태 확인...${NC}"
    
    if command -v gh &> /dev/null; then
        echo "GitHub CLI가 설치되어 있습니다."
        echo "최근 워크플로우 실행 상태:"
        gh run list --limit 5
    else
        echo -e "${YELLOW}GitHub CLI가 설치되어 있지 않습니다.${NC}"
        echo "설치 방법: https://cli.github.com/"
    fi
}

# Docker 이미지 상태 확인
check_docker_images() {
    echo -e "\n${BLUE}🐳 Docker 이미지 상태 확인...${NC}"
    
    if command -v docker &> /dev/null; then
        echo "로컬 Docker 이미지:"
        docker images | grep -E "(gateway|auth-service|chatbot-service)" || echo "로컬에 이미지가 없습니다."
        
        echo -e "\n실행 중인 컨테이너:"
        docker ps | grep -E "(gateway|auth-service|chatbot-service)" || echo "실행 중인 컨테이너가 없습니다."
    else
        echo -e "${RED}Docker가 설치되어 있지 않습니다.${NC}"
    fi
}

# 서비스 헬스체크
check_service_health() {
    echo -e "\n${BLUE}🏥 서비스 헬스체크...${NC}"
    
    local services=(
        "http://localhost:8080/health:Gateway"
        "http://localhost:8006/health:Chatbot Service"
        "http://localhost:8008/health:Auth Service"
    )
    
    for service in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service"
        
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name: 정상${NC}"
        else
            echo -e "${RED}❌ $name: 오류${NC}"
        fi
    done
}

# 환경 변수 확인
check_environment() {
    echo -e "\n${BLUE}🔧 환경 변수 확인...${NC}"
    
    local required_vars=(
        "VERCEL_TOKEN"
        "VERCEL_ORG_ID" 
        "VERCEL_PROJECT_ID"
        "RAILWAY_TOKEN"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -n "${!var}" ]; then
            echo -e "${GREEN}✅ $var: 설정됨${NC}"
        else
            echo -e "${YELLOW}⚠️ $var: 설정되지 않음${NC}"
        fi
    done
}

# 메인 실행
main() {
    echo -e "${GREEN}🚀 CI/CD 배포 상태 확인 시작${NC}"
    echo "=================================="
    
    check_environment
    check_github_actions
    check_docker_images
    check_service_health
    
    echo -e "\n${GREEN}✅ 상태 확인 완료${NC}"
    echo -e "\n${BLUE}💡 다음 단계:${NC}"
    echo "1. GitHub Secrets 설정 확인"
    echo "2. 코드를 main/develop 브랜치에 푸시"
    echo "3. GitHub Actions에서 워크플로우 실행 확인"
    echo "4. Vercel과 Railway에서 배포 상태 확인"
}

# 스크립트 실행
main "$@"
