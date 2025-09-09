import React from 'react';

const ProjectSummaryTab: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* 프로젝트 개요 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">🚀 ESG Mate 프로젝트 개요</h2>
        <p className="text-gray-600 leading-relaxed">
          <strong>ESG Mate</strong>는 기업의 ESG(환경, 사회, 거버넌스) 성과를 AI 기술로 분석하고, 
          TCFD 등 국제 표준에 맞는 전문 보고서를 자동으로 생성하는 통합 플랫폼입니다. 
          복잡한 ESG 분석 과정을 AI가 자동화하여 모든 기업이 쉽게 ESG 공시를 수행할 수 있도록 지원합니다.
        </p>
      </div>

      {/* 기술 스택 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">🛠️ 기술 스택</h2>
        
        {/* Frontend */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-blue-600 mb-3">Frontend</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-800">핵심 프레임워크</h4>
              <ul className="text-sm text-blue-700 mt-2 space-y-1">
                <li>• Next.js 15.4.5 - React 기반 풀스택 프레임워크</li>
                <li>• TypeScript 5.9.2 - 타입 안전성 보장</li>
                <li>• React 19.1.0 - 최신 UI 라이브러리</li>
              </ul>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <h4 className="font-semibold text-blue-800">스타일링 & 상태관리</h4>
              <ul className="text-sm text-blue-700 mt-2 space-y-1">
                <li>• Tailwind CSS 3.4.17 - 유틸리티 퍼스트 CSS</li>
                <li>• Zustand 5.0.7 - 경량 상태 관리</li>
                <li>• Next PWA 5.6.0 - Progressive Web App</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Backend */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-green-600 mb-3">Backend</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold text-green-800">웹 프레임워크 & 데이터베이스</h4>
              <ul className="text-sm text-green-700 mt-2 space-y-1">
                <li>• FastAPI - 고성능 Python 웹 프레임워크</li>
                <li>• PostgreSQL - 관계형 데이터베이스</li>
                <li>• Redis - 캐싱 및 세션 저장소</li>
              </ul>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-semibold text-green-800">비동기 처리 & ORM</h4>
              <ul className="text-sm text-green-700 mt-2 space-y-1">
                <li>• Celery - 비동기 작업 큐</li>
                <li>• SQLAlchemy - ORM 및 데이터베이스 추상화</li>
                <li>• asyncpg - 비동기 PostgreSQL 드라이버</li>
              </ul>
            </div>
          </div>
        </div>

        {/* AI/ML */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-purple-600 mb-3">AI/ML</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="font-semibold text-purple-800">LLM & RAG 시스템</h4>
              <ul className="text-sm text-purple-700 mt-2 space-y-1">
                <li>• LangChain - LLM 애플리케이션 프레임워크</li>
                <li>• ChromaDB - 벡터 데이터베이스</li>
                <li>• FAISS - Facebook AI Similarity Search</li>
                <li>• OpenAI API - GPT 모델 통합</li>
              </ul>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h4 className="font-semibold text-purple-800">임베딩 & 문서처리</h4>
              <ul className="text-sm text-purple-700 mt-2 space-y-1">
                <li>• Hugging Face - 오픈소스 AI 모델</li>
                <li>• Sentence Transformers - 텍스트 임베딩</li>
                <li>• PyPDFLoader - PDF 문서 파싱</li>
                <li>• RecursiveCharacterTextSplitter - 텍스트 청크 분할</li>
              </ul>
            </div>
          </div>
        </div>

        {/* DevOps */}
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-orange-600 mb-3">DevOps</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-orange-50 p-4 rounded-lg">
              <h4 className="font-semibold text-orange-800">컨테이너화 & 배포</h4>
              <ul className="text-sm text-orange-700 mt-2 space-y-1">
                <li>• Docker - 컨테이너화</li>
                <li>• Kubernetes - 컨테이너 오케스트레이션</li>
                <li>• Railway - 클라우드 배포 플랫폼</li>
                <li>• GitHub Actions - CI/CD 파이프라인</li>
              </ul>
            </div>
            <div className="bg-orange-50 p-4 rounded-lg">
              <h4 className="font-semibold text-orange-800">운영체제 & 문서생성</h4>
              <ul className="text-sm text-orange-700 mt-2 space-y-1">
                <li>• Debian 13 (trixie) - 컨테이너 운영체제</li>
                <li>• python-docx 1.1.0 - Word 문서 생성</li>
                <li>• WeasyPrint 61.2 - HTML to PDF 변환</li>
                <li>• 한글 폰트 패키지 - fonts-noto-cjk, fonts-nanum</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* 시스템 아키텍처 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">🏗️ 마이크로서비스 아키텍처</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">Gateway Service (8000)</h4>
            <p className="text-sm text-gray-600">API 게이트웨이, 서비스 디스커버리, 통합 인증</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">LLM Service (8002)</h4>
            <p className="text-sm text-gray-600">OpenAI GPT-4o-mini, KoAlpaca, RAG 시스템</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">RAG Service (8005)</h4>
            <p className="text-sm text-gray-600">FAISS 벡터 검색, PDF 처리, 문서 임베딩</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">TCFD Service (8003)</h4>
            <p className="text-sm text-gray-600">TCFD 프레임워크, 기후 시나리오 분석</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">Report Service (8004)</h4>
            <p className="text-sm text-gray-600">AI 보고서 생성, Word/PDF 다운로드</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold text-gray-800 mb-2">Auth Service (8008)</h4>
            <p className="text-sm text-gray-600">JWT 인증, 권한 관리, 사용자 데이터</p>
          </div>
        </div>
      </div>

      {/* 프로젝트 의의 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">🎯 프로젝트 의의</h2>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-blue-600 font-bold">1</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">ESG 분석의 민주화</h3>
              <p className="text-gray-600 text-sm">
                복잡한 ESG 표준과 데이터를 AI가 자동으로 분석하여 모든 기업이 쉽게 ESG 공시를 수행할 수 있도록 지원
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-green-600 font-bold">2</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">AI 기술의 실용적 활용</h3>
              <p className="text-gray-600 text-sm">
                RAG 시스템, 멀티 모달 AI, 실시간 문서 생성을 통해 ESG 분석의 복잡성을 단순화
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-purple-600 font-bold">3</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">국제 표준 준수</h3>
              <p className="text-gray-600 text-sm">
                TCFD 등 국제 ESG 표준을 준수하여 글로벌 기업들의 ESG 공시 요구사항 충족
              </p>
            </div>
          </div>
          <div className="flex items-start space-x-3">
            <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-orange-600 font-bold">4</span>
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">지속가능한 미래 지원</h3>
              <p className="text-gray-600 text-sm">
                기업들이 지속가능한 미래를 위한 의사결정을 내릴 수 있도록 데이터 기반 인사이트 제공
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 기대효과 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">📈 기대효과</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">비즈니스 임팩트</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start space-x-2">
                <span className="text-green-500">✓</span>
                <span>ESG 보고서 작성 시간 90% 단축</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-green-500">✓</span>
                <span>전문가 수준의 보고서 품질 보장</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-green-500">✓</span>
                <span>국제 표준 준수로 글로벌 경쟁력 향상</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-green-500">✓</span>
                <span>중소기업도 대기업 수준의 ESG 공시 가능</span>
              </li>
            </ul>
          </div>
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-800">기술적 혁신</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start space-x-2">
                <span className="text-blue-500">✓</span>
                <span>RAG 기반 지능형 문서 검색 시스템</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-500">✓</span>
                <span>마이크로서비스 아키텍처로 확장성 확보</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-500">✓</span>
                <span>실시간 AI 기반 보고서 생성</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="text-blue-500">✓</span>
                <span>행정구역별 맞춤형 기후 데이터 분석</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* 주요 기능 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">✨ 주요 기능</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
            <h4 className="font-semibold text-blue-800 mb-2">🤖 AI 기반 ESG 분석</h4>
            <p className="text-sm text-blue-700">자동 데이터 수집, 스마트 분석, 예측 모델링</p>
          </div>
          <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
            <h4 className="font-semibold text-green-800 mb-2">📊 표준 준수 보고서</h4>
            <p className="text-sm text-green-700">TCFD 보고서, AI 윤문, 섹션별 편집</p>
          </div>
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
            <h4 className="font-semibold text-purple-800 mb-2">📄 문서 다운로드</h4>
            <p className="text-sm text-purple-700">Word, PDF, HTML 다중 형식 지원</p>
          </div>
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 p-4 rounded-lg">
            <h4 className="font-semibold text-orange-800 mb-2">📈 대시보드 시각화</h4>
            <p className="text-sm text-orange-700">실시간 모니터링, 인터랙티브 차트</p>
          </div>
          <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg">
            <h4 className="font-semibold text-red-800 mb-2">🌍 기후 데이터 분석</h4>
            <p className="text-sm text-red-700">행정구역별 기후 데이터, 시나리오 분석</p>
          </div>
          <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 p-4 rounded-lg">
            <h4 className="font-semibold text-indigo-800 mb-2">🔐 보안 인증</h4>
            <p className="text-sm text-indigo-700">JWT 토큰, 회사별 데이터 격리</p>
          </div>
        </div>
      </div>

      {/* 로드맵 */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">🚀 개발 로드맵</h2>
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-green-600 mb-2">Phase 1 (현재) ✅</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
              <div>• 기본 MSA 아키텍처 구축</div>
              <div>• TCFD 보고서 생성 시스템</div>
              <div>• Word/PDF 다운로드 기능</div>
              <div>• 기본 AI 모델 통합</div>
              <div>• RAG 검색 시스템</div>
              <div>• 사용자 인증 시스템</div>
              <div>• 기후 데이터 시각화</div>
              <div>• 행정구역별 기후 데이터 분석</div>
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-blue-600 mb-2">Phase 2 (계획) 🔄</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
              <div>• 고급 데이터 시각화</div>
              <div>• 모바일 앱 개발</div>
              <div>• 다국어 지원 확대</div>
              <div>• 실시간 알림 시스템</div>
              <div>• 고급 분석 대시보드</div>
              <div>• 기후 시나리오 시뮬레이션</div>
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-purple-600 mb-2">Phase 3 (미래) 📋</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600">
              <div>• 블록체인 기반 데이터 검증</div>
              <div>• AI 예측 모델 고도화</div>
              <div>• 글로벌 ESG 표준 통합</div>
              <div>• 엔터프라이즈급 보안 강화</div>
              <div>• 머신러닝 기반 위험 예측</div>
              <div>• 자동화된 ESG 감사 시스템</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectSummaryTab;
