#!/bin/bash

# 🧪 서비스 테스트 스크립트
# 이 스크립트는 CI/CD에서 서비스들이 제대로 작동하는지 테스트합니다.

set -e

echo "🧪 서비스 테스트 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 테스트할 서비스들
SERVICES=(
    "http://localhost:8080/health:Gateway"
    "http://localhost:8006/health:Chatbot Service"
    "http://localhost:8008/health:Auth Service"
)

# 헬스체크 테스트
test_health_checks() {
    echo -e "\n${BLUE}🏥 헬스체크 테스트...${NC}"
    
    local failed=0
    
    for service in "${SERVICES[@]}"; do
        IFS=':' read -r url name <<< "$service"
        
        echo -n "테스트 중: $name... "
        
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ 성공${NC}"
        else
            echo -e "${RED}❌ 실패${NC}"
            failed=$((failed + 1))
        fi
    done
    
    if [ $failed -eq 0 ]; then
        echo -e "\n${GREEN}🎉 모든 서비스가 정상 작동 중입니다!${NC}"
        return 0
    else
        echo -e "\n${RED}❌ $failed 개의 서비스에서 문제가 발생했습니다.${NC}"
        return 1
    fi
}

# API 엔드포인트 테스트
test_api_endpoints() {
    echo -e "\n${BLUE}🔌 API 엔드포인트 테스트...${NC}"
    
    local failed=0
    
    # Gateway API 테스트
    echo -n "Gateway API 테스트... "
    if curl -s -f "http://localhost:8080/docs" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 성공${NC}"
    else
        echo -e "${RED}❌ 실패${NC}"
        failed=$((failed + 1))
    fi
    
    # Auth Service API 테스트
    echo -n "Auth Service API 테스트... "
    if curl -s -f "http://localhost:8008/docs" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 성공${NC}"
    else
        echo -e "${RED}❌ 실패${NC}"
        failed=$((failed + 1))
    fi
    
    # Chatbot Service API 테스트
    echo -n "Chatbot Service API 테스트... "
    if curl -s -f "http://localhost:8006/docs" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 성공${NC}"
    else
        echo -e "${RED}❌ 실패${NC}"
        failed=$((failed + 1))
    fi
    
    if [ $failed -eq 0 ]; then
        echo -e "\n${GREEN}🎉 모든 API 엔드포인트가 정상 작동 중입니다!${NC}"
        return 0
    else
        echo -e "\n${RED}❌ $failed 개의 API 엔드포인트에서 문제가 발생했습니다.${NC}"
        return 1"
    fi
}

# 메인 테스트 실행
main() {
    echo -e "${GREEN}🚀 서비스 테스트 시작${NC}"
    echo "=================================="
    
    # 서비스 시작 대기
    echo "서비스 시작을 기다리는 중... (30초)"
    sleep 30
    
    # 헬스체크 테스트
    if ! test_health_checks; then
        echo -e "\n${RED}❌ 헬스체크 테스트 실패${NC}"
        exit 1
    fi
    
    # API 엔드포인트 테스트
    if ! test_api_endpoints; then
        echo -e "\n${RED}❌ API 엔드포인트 테스트 실패${NC}"
        exit 1
    fi
    
    echo -e "\n${GREEN}✅ 모든 테스트가 성공적으로 완료되었습니다!${NC}"
}

# 스크립트 실행
main "$@"
