'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ClimateScenarioModal, TCFDDetailModal } from '@/ui/molecules';
import { Header } from '@/ui/organisms';
import { apiClient, tcfdReportAPI, tcfdAPI, llmServiceAPI } from '@/shared/lib';
import { downloadAsWordFromServer, downloadAsPDFFromServer, DownloadContent } from '@/utils/downloadUtils';
import ProjectSummaryTab from './components/ProjectSummaryTab';

import axios from 'axios';
// AI SDK는 Gateway를 통해 LLM Service를 호출하므로 불필요
// import { openai } from '@ai-sdk/openai';
// import { huggingface } from '@ai-sdk/huggingface';

// 컬럼명 한국어 매핑 객체
const COLUMN_LABELS: { [key: string]: string } = {
  // 1️⃣ 기업 정보
  id: '아이디',
  stock_code: '종목코드',
  companyname: '회사명',
  market: '시장',
  dart_code: 'DART 고유 코드',

  // 2️⃣ 재무 정보 (탭 문자 포함)
  '\tdebt': '부채',
  '\tdebt_ratio': '부채비율',
  '\tliability': '총부채',
  netdebt: '순부채',
  '\tnetdebt_ratio': '순부채비율',
  capital_stock: '자본금',
  '\tequity': '자본총계',
  '\tasset': '자산총계',
  'Long-term Debt': '장기부채',
  'Total Debt': '총부채',
  '\tcash': '현금',
  year: '연도',

  // 3️⃣ 임원 정보
  corp_code: '법인코드',
  nm: '성명',
  sexdstn: '성별',
  birth_ym: '생년월',
  ofcps: '직위(직책)',
  rgist_exctv_at: '등기임원 여부',
  fte_at: '상근 여부',
  chrg_job: '담당업무',
  main_career: '주요 경력',
  mxmm_shrholdr_relate: '최대주주와의 관계',
  hffc_pd: '재임 기간',
  tenure_end_on: '임기 종료일',

  // 4️⃣ 노동·급여 정보
  fo_bbm: '외국인 이사 수',
  rgllbr_co: '정규직 근로자 수',
  rgllbr_abacpt_labrr_co: '정규직 외 수탁/용역 근로자 수',
  cnttk_co: '계약직 근로자 수',
  cnttk_abacpt_labrr_co: '계약직 외 수탁/용역 근로자 수',
  sm: '소속 노동조합 조합원 수',
  avrg_cnwk_sdytrn: '평균 근속연수',
  fyer_salary_totamt: '연간 급여 총액',
  jan_salary_am: '1인당 평균 급여액',

  // 5️⃣ 손익계산 정보
  revenue: '매출액',
  sales: '매출',
  cost_of_sales: '매출원가',
  gross_profit: '매출총이익',
  operating_expenses: '영업비용',
  operating_income: '영업이익',
  non_operating_income: '영업외수익',
  non_operating_expenses: '영업외비용',
  net_income: '당기순이익',
  ebitda: 'EBITDA',
  ebit: 'EBIT',
  net_profit: '순이익',
  total_revenue: '총매출',
  total_cost: '총비용',
  profit_margin: '이익률',
  return_on_equity: 'ROE',
  return_on_assets: 'ROA',
  earnings_per_share: 'EPS',
  book_value_per_share: 'BPS',
  price_to_book: 'PBR',
  price_to_earnings: 'PER',
  
  // 6️⃣ 손익계산서 헤더 컬럼명
  metric_name: '지표명',
  fiscal_year_current: '현재 회계연도',
  fiscal_year_previous: '이전 회계연도',
  fiscal_year_before_last: '재작년 회계연도',
};

// 컬럼명을 한국어로 변환하는 함수
const getKoreanLabel = (englishLabel: string): string => {
  console.log('🔍 컬럼명 변환:', englishLabel, '→', COLUMN_LABELS[englishLabel] || englishLabel);
  return COLUMN_LABELS[englishLabel] || englishLabel;
};

// TCFD 표준 데이터 타입 정의
export interface TCFDStandardData {
  // id 필드 제거 (실제 DB에 없음)
  category: string;
  disclosure_id: string;
  disclosure_summary: string;
  disclosure_detail: string;
}

// TCFD 프레임워크 카테고리별 데이터 그룹화
interface TCFDFrameworkData {
  [category: string]: {
    title: string;
    description: string;
    color: string;
    bgColor: string;
    disclosures: TCFDStandardData[];
  };
}

// 테이블 데이터 타입 정의
interface TableRecord {
  id: string;
  [key: string]: string | number | boolean;
}



export default function TcfdSrPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState(0);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userCompanyName, setUserCompanyName] = useState<string | null>(null); // 사용자 회사이름 추가
  
  // JWT 토큰에서 사용자 정보 파싱하는 함수
  const parseUserFromToken = () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) return null;
      
      // JWT 토큰의 payload 부분 파싱 (base64 디코딩)
      const payload = token.split('.')[1];
      if (!payload) return null;
      
      const decodedPayload = JSON.parse(atob(payload));
      return decodedPayload;
    } catch (error) {
      console.error('토큰 파싱 오류:', error);
      return null;
    }
  };

  // 회사 검색 관련 상태
  const [companyName, setCompanyName] = useState(''); // 빈 문자열로 초기화
  const [companyFinancialData, setCompanyFinancialData] = useState<any>(null);
  const [companyOverview, setCompanyOverview] = useState<any>(null);
  const [companyError, setCompanyError] = useState<string | null>(null);
  const [isLoadingCompany, setIsLoadingCompany] = useState(false);

  // 더보기 상태 관리
  const [showAllStates, setShowAllStates] = useState<{ [key: string]: boolean }>({});

  // 상세보기 모달 상태 추가
  const [selectedScenario, setSelectedScenario] = useState<'ssp2.6' | 'ssp8.5' | null>(null);
  const [isClimateModalOpen, setIsClimateModalOpen] = useState(false);

  // TCFD 상세보기 모달 상태 추가
  const [isTcfdDetailModalOpen, setIsTcfdDetailModalOpen] = useState(false);
  const [selectedTcfdCategory, setSelectedTcfdCategory] = useState<{
    category: string;
    title: string;
    description: string;
    disclosures: TCFDStandardData[];
    color: string;
    bgColor: string;
  } | null>(null);

  // 이용가이드 박스 상태 추가
  const [isGuideOpen, setIsGuideOpen] = useState(false);

  // TCFD 표준 데이터 상태 추가
  const [tcfdStandards, setTcfdStandards] = useState<TCFDFrameworkData>({});
  const [isLoadingTcfd, setIsLoadingTcfd] = useState(false);
  const [tcfdError, setTcfdError] = useState<string | null>(null);

  // TCFD 입력 데이터 상태 관리
  const [tcfdInputData, setTcfdInputData] = useState({
    governance_g1: '',
    governance_g2: '',
    strategy_s1: '',
    strategy_s2: '',
    strategy_s3: '',
    risk_management_r1: '',
    risk_management_r2: '',
    risk_management_r3: '',
    metrics_targets_m1: '',
    metrics_targets_m2: '',
    metrics_targets_m3: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // RAG 결과 상태 관리
  const [ragResults, setRagResults] = useState<{
    openai: any | null;
    huggingface: any | null;
  }>({
    openai: null,
    huggingface: null
  });
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedLLMModel, setSelectedLLMModel] = useState<'openai' | 'huggingface' | null>(null);
  const [tcfdDatabaseData, setTcfdDatabaseData] = useState<any>(null);
  const [isLoadingDatabaseData, setIsLoadingDatabaseData] = useState(false);

  // 기후시나리오 관련 상태 추가
  const [selectedYear, setSelectedYear] = useState<'2026-2030' | '2025-2035-2050'>('2026-2030');
  const [selectedSSP, setSelectedSSP] = useState<'SSP126' | 'SSP585'>('SSP126');
  const [selectedRegion, setSelectedRegion] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'temperature' | 'precipitation' | 'extreme'>('all');
  const [isImageModalOpen, setIsImageModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState<{ src: string; title: string } | null>(null);
  
  // 기후 데이터 생성 모달 관련 상태 추가
  const [showClimateDataModal, setShowClimateDataModal] = useState(false);
  const [climateDataSettings, setClimateDataSettings] = useState<{
    scenario: string;
    variable: string;
    startYear: number;
    endYear: number;
    region: string;
    additionalYears: number[];
  }>({
    scenario: 'SSP126',
    variable: 'HW33',
    startYear: 2021,
    endYear: 2030,
    region: '전체 지역',
    additionalYears: [] // 추가 연도 배열
  });
  const [generatedClimateData, setGeneratedClimateData] = useState<string | null>(null);
  const [isGeneratingClimateData, setIsGeneratingClimateData] = useState(false);
  
  // 행정구역 관련 상태
  const [administrativeRegions, setAdministrativeRegions] = useState<Array<{region_code: string, region_name: string, sub_region_name: string}>>([]);
  const [regionSearchTerm, setRegionSearchTerm] = useState('');
  const [filteredRegions, setFilteredRegions] = useState<Array<{region_code: string, region_name: string, sub_region_name: string}>>([]);
  const [showRegionDropdown, setShowRegionDropdown] = useState(false);
  
  // 도움말 모달 관련 상태
  const [isHelpModalOpen, setIsHelpModalOpen] = useState(false);
  const [isScenarioModalOpen, setIsScenarioModalOpen] = useState(false);

  // 추가 연도 관리 함수들
  const addAdditionalYear = () => {
    setClimateDataSettings(prev => ({
      ...prev,
      additionalYears: [...prev.additionalYears, 2025] // 기본값 2025
    }));
  };

  const removeAdditionalYear = (index: number) => {
    setClimateDataSettings(prev => ({
      ...prev,
      additionalYears: prev.additionalYears.filter((_, i) => i !== index)
    }));
  };

  const updateAdditionalYear = (index: number, year: number) => {
    setClimateDataSettings(prev => ({
      ...prev,
      additionalYears: prev.additionalYears.map((y, i) => i === index ? year : y)
    }));
  };

  // 회사 목록 로드 (사용하지 않음)
  const loadCompanies = async () => {
    // 회사 목록은 더 이상 로드하지 않음
  };

  // 회사별 재무정보 로드 (apiClient 사용)
  const loadCompanyFinancialData = async (companyName: string) => {
    if (!companyName.trim()) return;

    // 사용자 회사이름과 일치하는지 확인
    if (userCompanyName && companyName.trim() !== userCompanyName.trim()) {
      setCompanyError(`접근 권한이 없습니다. 회원가입 시 입력한 회사이름 "${userCompanyName}"만 검색 가능합니다.`);
      return;
    }

    setIsLoadingCompany(true);
    setCompanyError(null);
    setSelectedRegion(''); // 회사 변경 시 지역 선택 초기화
    setSelectedCategory('all'); // 회사 변경 시 카테고리 선택 초기화

    // 디버깅 로그 추가
    console.log('🔍 회사명:', companyName);
    console.log('🔍 인코딩된 회사명:', encodeURIComponent(companyName));

    try {
      // 먼저 기업개요 정보 조회
      const overviewResponse = await tcfdAPI.getCompanyOverview(companyName);
      console.log('🔍 기업개요 응답:', overviewResponse);
      
      if (overviewResponse.data.success && overviewResponse.data.overview) {
        // 기업개요 정보가 있으면 회사정보 탭에 표시
        setCompanyOverview(overviewResponse.data.overview);
      }

      // 재무정보 조회
      const url = `/api/v1/tcfd/company-financial-data?company_name=${encodeURIComponent(
        companyName,
      )}`;
      console.log('🔍 요청 URL:', url);

      const response = await apiClient.get(url);
      console.log('🔍 응답 상태:', response.status);
      console.log('🔍 응답 데이터:', response.data);

      const data = response.data;

      if (data.success === false) {
        throw new Error(data.error || '재무정보를 불러올 수 없습니다');
      }

      setCompanyFinancialData(data);
      console.log('✅ 데이터 설정 완료:', data);
      console.log('✅ 데이터 구조 확인:');
      console.log('  - success:', data.success);
      console.log('  - company_name:', data.company_name);
      console.log('  - total_records:', data.total_records);
      console.log('  - tables:', data.tables);
      console.log('  - data keys:', Object.keys(data.data || {}));
      console.log('  - employee data length:', data.data?.employee?.length);
      console.log('  - profit data length:', data.data?.profit?.length);
      console.log('  - executive data length:', data.data?.executive?.length);
      console.log('  - financial data length:', data.data?.financial?.length);
      console.log('  - corporation data length:', data.data?.corporation?.length);

      // 재무정보 로드 완료 시 자동으로 재무정보 탭으로 이동
      setActiveTab(2);
      
    } catch (error) {
      console.error('❌ 회사 정보 로드 실패:', error);
      setCompanyError(error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다');
    } finally {
      setIsLoadingCompany(false);
    }
  };



  // TCFD 데이터베이스에서 입력 데이터 가져오기 (created_at 기준 최신 데이터)
  const loadTcfdDatabaseData = async () => {
    if (!companyFinancialData?.company_name) {
      console.log('❌ 회사 정보가 없습니다');
      return null;
    }

    setIsLoadingDatabaseData(true);
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('인증 토큰이 없습니다');
      }

      // TCFD 입력 데이터 조회 API 호출 (가장 최신 데이터 기준)
      const response = await fetch(`${process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8000'}/api/v1/tcfd/inputs`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('✅ TCFD 데이터베이스 데이터 로드 성공:', data);
      
      if (data.success && data.data) {
        // 배열인 경우 가장 최신 데이터(created_at 기준)를 찾기
        let latestData;
        if (Array.isArray(data.data)) {
          if (data.data.length === 0) {
            console.log('❌ TCFD 데이터가 없습니다');
            return null;
          }
          
          // created_at 기준으로 정렬하여 가장 최신 데이터 선택
          latestData = data.data.sort((a: any, b: any) => {
            const dateA = new Date(a.created_at || 0);
            const dateB = new Date(b.created_at || 0);
            return dateB.getTime() - dateA.getTime(); // 내림차순 정렬 (최신이 먼저)
          })[0];
          
          console.log('📅 전체 데이터 개수:', data.data.length);
          console.log('📅 최신 데이터 생성일시:', latestData.created_at);
        } else {
          // 단일 객체인 경우
          latestData = data.data;
          console.log('📅 단일 데이터 생성일시:', latestData.created_at);
        }
        
        setTcfdDatabaseData(latestData);
        return latestData;
      } else {
        console.log('❌ TCFD 데이터가 없습니다');
        return null;
      }
    } catch (error) {
      console.error('❌ TCFD 데이터베이스 데이터 로드 실패:', error);
      return null;
    } finally {
      setIsLoadingDatabaseData(false);
    }
  };

  // 상세보기 모달 열기/닫기
  const handleClimateDetails = (scenario: 'ssp2.6' | 'ssp8.5') => {
    setSelectedScenario(scenario);
    setIsClimateModalOpen(true);
  };
  const closeClimateModal = () => {
    setIsClimateModalOpen(false);
    setSelectedScenario(null);
  };

  // 도움말 모달 열기/닫기
  const openHelpModal = () => setIsHelpModalOpen(true);
  const closeHelpModal = () => setIsHelpModalOpen(false);
  const openScenarioModal = () => setIsScenarioModalOpen(true);
  const closeScenarioModal = () => setIsScenarioModalOpen(false);

  // 이미지 다운로드 함수
  const downloadImage = (imageSrc: string, imageTitle: string) => {
    const link = document.createElement('a');
    link.href = imageSrc;
    link.download = `${imageTitle}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // TCFD 입력 데이터 변경 핸들러
  const handleTcfdInputChange = (field: string, value: string) => {
    setTcfdInputData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  // TCFD 데이터 제출 함수
  const handleTcfdSubmit = async () => {
    if (!companyFinancialData?.company_name) {
      alert('회사 정보가 필요합니다. 먼저 회사를 검색해주세요.');
      return;
    }

    // 인증 상태 확인
    const token = localStorage.getItem('auth_token');
    if (!token) {
      alert('로그인이 필요합니다. 먼저 로그인해주세요.');
      router.push('/login');
      return;
    }

    setIsSubmitting(true);
    try {
      const submitData = {
        company_name: companyFinancialData.company_name,
        user_id: 'user123', // 임시 사용자 ID
        ...tcfdInputData,
      };

      console.log('📤 TCFD 데이터 제출:', submitData);
      console.log('🔐 인증 토큰:', token ? '존재함' : '없음');

      const response = await tcfdReportAPI.createTcfdInput(submitData);
      console.log('✅ TCFD 데이터 저장 성공:', response.data);

      alert('TCFD 데이터가 성공적으로 저장되었습니다!');

      // 입력 필드 초기화
      setTcfdInputData({
        governance_g1: '',
        governance_g2: '',
        strategy_s1: '',
        strategy_s2: '',
        strategy_s3: '',
        risk_management_r1: '',
        risk_management_r2: '',
        risk_management_r3: '',
        metrics_targets_m1: '',
        metrics_targets_m2: '',
        metrics_targets_m3: '',
      });
    } catch (error: any) {
      console.error('❌ TCFD 데이터 저장 실패:', error);
      if (error.response?.status === 401) {
        alert('인증이 만료되었습니다. 다시 로그인해주세요.');
        router.push('/login');
      } else {
        alert('TCFD 데이터 저장에 실패했습니다. 다시 시도해주세요.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // 새로운 state 변수들 추가
  const [generatingReport, setGeneratingReport] = useState(false);
  const [reportGenerationStatus, setReportGenerationStatus] = useState('');
  const [generatedReport, setGeneratedReport] = useState<string>('');

  // 2개 RAG 시스템으로 TCFD 보고서 생성 함수
  const handleGenerateTCFDReport = async () => {
    if (!companyFinancialData?.company_name) {
      alert('회사 정보를 먼저 검색해주세요.');
      return;
    }

    try {
      setGeneratingReport(true);
      setReportGenerationStatus('보고서 생성 중...');

      // TCFD 데이터베이스에서 데이터 가져오기
      let dbData = tcfdDatabaseData;
      
      if (!dbData) {
        console.log('🔄 데이터베이스에서 TCFD 데이터를 자동으로 가져와서 최신 데이터를 선택합니다...');
        dbData = await loadTcfdDatabaseData();
      }
      
      if (!dbData) {
        alert('TCFD 프레임워크에서 입력한 데이터를 찾을 수 없습니다. 먼저 TCFD 프레임워크 탭에서 데이터를 입력하고 저장해주세요.');
        setGeneratingReport(false);
        return;
      }

      // 1. TCFD 입력 데이터를 tcfd_inputs 테이블에 저장
      const tcfdInputData = {
        company_name: companyFinancialData.company_name,
        user_id: localStorage.getItem('user_id') || 'user123',
        governance_g1: dbData.governance_g1 || '',
        governance_g2: dbData.governance_g2 || '',
        strategy_s1: dbData.strategy_s1 || '',
        strategy_s2: dbData.strategy_s2 || '',
        strategy_s3: dbData.strategy_s3 || '',
        risk_management_r1: dbData.risk_management_r1 || '',
        risk_management_r2: dbData.risk_management_r2 || '',
        risk_management_r3: dbData.risk_management_r3 || '',
        metrics_targets_m1: dbData.metrics_targets_m1 || '',
        metrics_targets_m2: dbData.metrics_targets_m2 || '',
        metrics_targets_m3: dbData.metrics_targets_m3 || '',
      };

      console.log('📝 TCFD 입력 데이터 저장 시작:', tcfdInputData);

      const inputResponse = await tcfdReportAPI.createTcfdInputs(tcfdInputData);
      console.log('✅ TCFD 입력 데이터 저장 완료:', inputResponse.data);

      // 2. TCFD Draft 데이터를 tcfd_drafts 테이블에 저장
      const tcfdDraftData = {
        company_name: companyFinancialData.company_name,
        user_id: localStorage.getItem('user_id') || 'user123',
        tcfd_input_id: inputResponse.data.data.id, // 저장된 입력 데이터의 ID
        draft_content: `TCFD 보고서 초안 - ${companyFinancialData.company_name}`,
        draft_type: 'draft',
        file_path: null,
        status: 'processing'
      };

      console.log('📝 TCFD Draft 데이터 저장 시작:', tcfdDraftData);

      const draftResponse = await tcfdReportAPI.createTcfdDraft(tcfdDraftData);
      console.log('✅ TCFD Draft 데이터 저장 완료:', draftResponse.data);

      // 3. Draft 상태를 'completed'로 업데이트
      await tcfdReportAPI.updateDraftStatus(draftResponse.data.data.id, { status: 'completed' });

      // 4. 기존 TCFD 보고서 생성 로직 (기존 코드 보존)
      const tcfdReportRequest = {
        company_name: companyFinancialData.company_name,
        report_year: new Date().getFullYear().toString(),
        tcfd_inputs: {
          company_name: companyFinancialData.company_name,
          user_id: localStorage.getItem('user_id') || 'user123',
          governance_g1: dbData.governance_g1 || '',
          governance_g2: dbData.governance_g2 || '',
          strategy_s1: dbData.strategy_s1 || '',
          strategy_s2: dbData.strategy_s2 || '',
          strategy_s3: dbData.strategy_s3 || '',
          risk_management_r1: dbData.risk_management_r1 || '',
          risk_management_r2: dbData.risk_management_r2 || '',
          risk_management_r3: dbData.risk_management_r3 || '',
          metrics_targets_m1: dbData.metrics_targets_m1 || '',
          metrics_targets_m2: dbData.metrics_targets_m2 || '',
          metrics_targets_m3: dbData.metrics_targets_m3 || '',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        report_type: "draft",
        llm_provider: "openai"
      };

      console.log('🤖 TCFD 보고서 생성 시작:', tcfdReportRequest);
      console.log('🎯 선택된 LLM 모델:', selectedLLMModel);

      // 선택된 LLM 모델로 TCFD 보고서 생성
      let result: any = null;
      try {
        if (selectedLLMModel === "openai") {
          console.log('🚀 OpenAI API 호출 시작...');
          // OpenAI API 호출 (기존 로직 보존)
          result = await generateTCFDReportWithLLM(tcfdReportRequest, "openai");
          console.log('✅ OpenAI TCFD 보고서 결과:', result);
        } else {
          console.log('🚀 Hugging Face API 호출 시작...');
          // Hugging Face API 호출 (기존 로직 보존)
          result = await generateTCFDReportWithLLM(tcfdReportRequest, "huggingface");
          console.log('✅ Hugging Face TCFD 보고서 결과:', result);
        }
      } catch (llmError) {
        console.error('❌ LLM API 호출 실패:', llmError);
        throw new Error(`LLM API 호출 실패: ${llmError instanceof Error ? llmError.message : String(llmError)}`);
      }

      // 5. Draft 내용을 실제 생성된 보고서로 업데이트
      const generatedContent = result?.report_content || '보고서 생성에 실패했습니다.';

      await tcfdReportAPI.updateDraftStatus(draftResponse.data.data.id, { status: 'completed' });

      setGeneratedReport(generatedContent);
      setReportGenerationStatus('보고서 생성 완료!');
      
      // 성공 메시지 표시
      alert('TCFD 보고서가 성공적으로 생성되었습니다!');

    } catch (error) {
      console.error('❌ TCFD 보고서 생성 실패:', error);
      setReportGenerationStatus('보고서 생성 실패');
      alert('TCFD 보고서 생성에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setGeneratingReport(false);
    }
  };

  // LLM 서비스를 사용하여 TCFD 보고서 생성
  const generateTCFDReportWithLLM = async (request: any, llmProvider: string) => {
    try {
      console.log(`🚀 ${llmProvider} TCFD 보고서 생성 시작`);
      
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('인증 토큰이 없습니다');
      }

      // 환경에 따라 Gateway URL 결정 (Docker vs Railway)
      const gatewayUrl = process.env.NEXT_PUBLIC_GATEWAY_URL || 
        (window.location.hostname === 'localhost' ? 'http://localhost:8080' : 'https://autosr-production.up.railway.app');
      
      console.log('🌐 Gateway URL 결정:', gatewayUrl);
      console.log('🌐 현재 호스트:', window.location.hostname);
      console.log('📤 요청 데이터:', request);
      
      const apiUrl = `${gatewayUrl}/api/v1/tcfd/generate-report`;
      console.log('🎯 API 엔드포인트:', apiUrl);
      
      // Gateway를 통해 LLM Service의 TCFD API 호출
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...request,
          llm_provider: llmProvider
        })
      });

      console.log('📥 응답 상태:', response.status);
      console.log('📥 응답 헤더:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ HTTP 오류 응답:', errorText);
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
      }

      const result = await response.json();
      console.log('✅ 응답 데이터:', result);
      return result;
    } catch (error: unknown) {
      console.error(`❌ ${llmProvider} TCFD 보고서 생성 실패:`, error);
      return {
        success: false,
        report_content: `${llmProvider} 모델로 보고서 생성에 실패했습니다: ${error instanceof Error ? error.message : String(error)}`,
        error_message: error instanceof Error ? error.message : String(error)
      };
    }
  };

  // TCFD 상세보기 모달 열기/닫기
  const handleTcfdDetails = (
    category: string,
    data: {
      title: string;
      description: string;
      disclosures: TCFDStandardData[];
      color: string;
      bgColor: string;
    },
  ) => {
    setSelectedTcfdCategory({
      category,
      title: data.title,
      description: data.description,
      disclosures: data.disclosures,
      color: data.color,
      bgColor: data.bgColor,
    });
    setIsTcfdDetailModalOpen(true);
  };
  const closeTcfdDetailModal = () => {
    setIsTcfdDetailModalOpen(false);
    setSelectedTcfdCategory(null);
  };

  // Word 다운로드 함수
  const handleDownloadAsWord = async (modelType: 'openai' | 'huggingface') => {
    try {
      const result = ragResults[modelType];
      if (!result) {
        alert('다운로드할 내용이 없습니다.');
        return;
      }

      const content: DownloadContent = {
        title: `${tcfdDatabaseData?.company_name || '회사'} TCFD 보고서 - ${modelType === 'openai' ? 'OpenAI GPT-4o-mini' : 'KoAlpaca/RoLA'}`,
        draft: result.draft,
        polished: result.polished,
        companyName: tcfdDatabaseData?.company_name,
        timestamp: new Date().toLocaleString('ko-KR')
      };

      // 다운로드 시작 알림
      console.log('Word 다운로드 시작:', content.title);
      
      await downloadAsWordFromServer(content);
      
      // 성공 알림
      console.log('Word 다운로드 완료');
    } catch (error) {
      console.error('Word 다운로드 실패:', error);
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
      alert(`Word 문서 다운로드에 실패했습니다: ${errorMessage}`);
    }
  };

  // PDF 다운로드 함수
  const handleDownloadAsPDF = async (modelType: 'openai' | 'huggingface') => {
    try {
      const result = ragResults[modelType];
      if (!result) {
        alert('다운로드할 내용이 없습니다.');
        return;
      }

      const content: DownloadContent = {
        title: `${tcfdDatabaseData?.company_name || '회사'} TCFD 보고서 - ${modelType === 'openai' ? 'OpenAI GPT-4o-mini' : 'KoAlpaca/RoLA'}`,
        draft: result.draft,
        polished: result.polished,
        companyName: tcfdDatabaseData?.company_name,
        timestamp: new Date().toLocaleString('ko-KR')
      };

      // 다운로드 시작 알림
      console.log('PDF 다운로드 시작:', content.title);
      
      await downloadAsPDFFromServer(content);
      
      // 성공 알림
      console.log('PDF 다운로드 완료');
    } catch (error) {
      console.error('PDF 다운로드 실패:', error);
      const errorMessage = error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.';
      alert(`PDF 다운로드에 실패했습니다: ${errorMessage}`);
    }
  };

  // TCFD 표준 데이터 불러오기 (apiClient 사용)
  const fetchTcfdStandards = async () => {
    setIsLoadingTcfd(true);
    setTcfdError(null);
    try {
      // 인증 토큰 확인
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('인증 토큰이 없습니다');
      }

      console.log('🔍 TCFD 표준 데이터 로드 시작 (토큰 존재)');

      // Gateway를 통해 TCFD 표준 정보 조회
      const response = await tcfdAPI.getTcfdStandards();
      console.log('🔍 TCFD 응답 전체:', response.data);

      // 응답 구조에 맞게 data 추출
      const responseData = response.data;
      const data: TCFDStandardData[] = responseData.data || [];

      console.log('🔍 TCFD 데이터 배열:', data);

      // 데이터를 카테고리별로 그룹화하고 TCFD 프레임워크에 맞게 구성
      const frameworkData: TCFDFrameworkData = {
        지배구조: {
          title: '거버넌스',
          description: '기후 관련 위험과 기회에 대한 감독 및 책임',
          color: 'text-blue-700',
          bgColor: 'bg-blue-50',
          disclosures: [],
        },
        전략: {
          title: '전략',
          description: '기후 관련 위험과 기회가 비즈니스 모델에 미치는 영향',
          color: 'text-green-700',
          bgColor: 'bg-green-50',
          disclosures: [],
        },
        위험관리: {
          title: '리스크 관리',
          description: '기후 관련 위험 식별, 평가 및 관리',
          color: 'text-yellow-700',
          bgColor: 'bg-yellow-50',
          disclosures: [],
        },
        '지표와 감축목표': {
          title: '지표 및 목표',
          description:
            '기후 관련 위험과 기회를 평가하고 관리하기 위한 지표 및 목표',
          color: 'text-purple-700',
          bgColor: 'bg-purple-50',
          disclosures: [],
        },
      };

      // 데이터를 각 카테고리에 분류
      data.forEach((item) => {
        if (frameworkData[item.category]) {
          frameworkData[item.category].disclosures.push(item);
        }
      });

      setTcfdStandards(frameworkData);
    } catch (err) {
      console.error('Failed to fetch TCFD standards:', err);
      if (axios.isAxiosError(err)) {
        setTcfdError(`TCFD 표준 정보 로드 실패: ${err.response?.status} - ${err.message}`);
      } else {
        setTcfdError('TCFD 표준 정보를 불러오는 데 실패했습니다.');
      }
    } finally {
      setIsLoadingTcfd(false);
    }
  };

  // 컴포넌트 마운트 시 회사 목록 로드
  useEffect(() => {
    loadCompanies();
  }, []);

  // user 정보가 변경될 때 userCompanyName 설정
  useEffect(() => {
    const userData = parseUserFromToken();
    if (userData && userData.company_id) {
      setUserCompanyName(userData.company_id);
      console.log('🏢 JWT에서 파싱한 사용자 회사이름:', userData.company_id);
    }
  }, []);

  // 인증 상태 확인 (개선된 버전)
  useEffect(() => {
    // 클라이언트 사이드에서만 인증 확인
    if (typeof window !== 'undefined') {
      const checkAuth = async () => {
        try {
          // localStorage에서 토큰 확인
          const token = localStorage.getItem('auth_token');
          if (!token) {
            console.log('❌ 인증 토큰이 없습니다');
            router.push('/login');
            return;
          }

          // 토큰이 있으면 인증 상태 설정
          console.log('🔍 토큰 존재, 인증 상태 설정');
            setIsAuthenticated(true);

          // TCFD 표준 데이터 로드
            console.log('🔍 TCFD 표준 데이터 로드 시작...');
            await fetchTcfdStandards();
        } catch (error: any) {
          console.error('❌ 인증 확인 실패:', error);
          if (error.response?.status === 401) {
            alert('인증이 만료되었습니다. 다시 로그인해주세요.');
            localStorage.removeItem('auth_token');
            router.push('/login');
          }
        }
      };

      checkAuth();
    }
  }, [router]);

  // 페이지 포커스 시 인증 상태 재확인 (선택적)
  useEffect(() => {
    const handleFocus = () => {
      // 페이지가 포커스될 때 간단한 토큰 존재 여부만 확인
      const token = localStorage.getItem('auth_token');
      if (token && !isAuthenticated) {
        console.log('🔍 페이지 포커스 시 인증 상태 복원');
        setIsAuthenticated(true);
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [isAuthenticated]);

  // 재무정보 표시 컴포넌트
  const renderFinancialTable = (data: TableRecord[] | undefined, title: string) => {
    console.log(`🔍 ${title} 렌더링:`, data);

    if (!data || data.length === 0) {
      console.log(`❌ ${title}: 데이터 없음`);
      return <div className="text-center py-4 text-gray-500">{title} 데이터가 없습니다</div>;
    }

    console.log(`✅ ${title}: ${data.length}개 레코드`);

    const columns = Object.keys(data[0] || {});
    console.log(`🔍 ${title} 컬럼명:`, columns);

    // 재무상태, 기업 정보, 직원정보, 임원정보는 세로형태로 표시
    if (
      title === '재무상태' ||
      title === '기업 정보' ||
      title === '직원 정보' ||
      title === '임원 정보'
    ) {
      const showAll = showAllStates[title] || false;
      const displayData = showAll ? data : data.slice(0, 6);
      const hasMore = data.length > 6;

      return (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-primary-600">{title}</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {displayData.map((row, index) => {
              // 레코드 이름을 의미있게 생성
              let recordName = `레코드 ${index + 1}`;

              if (title === '재무상태' && (row as any).companyname) {
                recordName = String((row as any).companyname);
              } else if (title === '기업 정보' && (row as any).companyname) {
                recordName = String((row as any).companyname);
              } else if (title === '직원 정보' && (row as any).name) {
                recordName = String((row as any).name);
              } else if (title === '임원 정보' && (row as any).name) {
                recordName = String((row as any).name);
              } else if ((row as any).id) {
                recordName = `ID: ${String((row as any).id)}`;
              }

              return (
                <div
                  key={index}
                  className="bg-gray-100 border border-gray-300 rounded-brand p-4 shadow-soft"
                >
                  <h4 className="font-medium text-gray-900 mb-3 text-sm">{recordName}</h4>
                  <div className="space-y-2">
                    {columns.map((column) => (
                      <div key={column} className="flex justify-between">
                        <span className="text-xs font-medium text-gray-600 capitalize">
                          {getKoreanLabel(column)}:
                        </span>
                        <span className="text-sm text-gray-900 text-right break-words max-w-[200px]">
                          {typeof (row as any)[column] === 'number'
                            ? ((row as any)[column] as number).toLocaleString()
                            : String((row as any)[column] ?? '-')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>

          {/* 더보기 버튼 */}
          {hasMore && (
            <div className="mt-4 text-center">
              <button
                onClick={() => setShowAllStates((prev) => ({ ...prev, [title]: !showAll }))}
                className="px-6 py-2 bg-primary-600 text-white rounded-brand shadow-soft hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-100"
              >
                {showAll ? '접기' : `더보기 (${data.length - 6}개 더)`}
              </button>
            </div>
          )}
        </div>
      );
    }

    // 손익계산만 기존 테이블 형태로 표시
    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-3 text-primary-600">{title}</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-300 rounded-brand shadow-soft">
            <thead className="bg-gray-100">
              <tr>
                {columns.map((column) => (
                  <th
                    key={column}
                    className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-b border-gray-300"
                  >
                    {getKoreanLabel(column)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-300">
              {data.map((row, index) => (
                <tr key={index} className="hover:bg-gray-100">
                  {columns.map((column) => (
                    <td key={column} className="px-4 py-2 text-sm text-gray-900 border-b border-gray-300">
                      {typeof (row as any)[column] === 'number'
                        ? ((row as any)[column] as number).toLocaleString()
                        : String((row as any)[column] ?? '-')}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  // TCFD 권고사항별 AI 문장 생성 함수
  const handleGenerateRecommendation = async (recommendationType: string, llmProvider: string) => {
    if (!companyFinancialData?.company_name) {
      alert('회사 정보가 필요합니다. 먼저 회사를 검색해주세요.');
      return;
    }

    const userInput = tcfdInputData[`${getRecommendationKey(recommendationType)}` as keyof typeof tcfdInputData];
    if (!userInput.trim()) {
      alert('해당 권고사항에 대한 입력 데이터가 필요합니다. 먼저 데이터를 입력해주세요.');
      return;
    }

    try {
      let result;
      if (llmProvider === 'openai') {
        result = await llmServiceAPI.generateTCFDRecommendationOpenAI(
          companyFinancialData.company_name,
          recommendationType,
          userInput
        );
      } else {
        result = await llmServiceAPI.generateTCFDRecommendationKoAlpaca(
          companyFinancialData.company_name,
          recommendationType,
          userInput
        );
      }

      if (result.success && result.generated_text) {
        // 생성된 문장을 해당 입력 필드에 자동으로 채우기
        const fieldKey = getRecommendationKey(recommendationType);
        setTcfdInputData(prev => ({
          ...prev,
          [fieldKey]: result.generated_text
        }));
        
        alert(`${llmProvider === 'openai' ? 'OpenAI' : 'KoAlpaca'}로 생성된 문장이 입력 필드에 적용되었습니다.`);
      } else {
        alert(`문장 생성에 실패했습니다: ${result.error_message || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('TCFD 권고사항 문장 생성 실패:', error);
      alert('문장 생성 중 오류가 발생했습니다.');
    }
  };

  // 권고사항 타입을 입력 필드 키로 변환하는 함수
  const getRecommendationKey = (recommendationType: string): string => {
    const keyMapping: { [key: string]: string } = {
      'g1': 'governance_g1',
      'g2': 'governance_g2',
      's1': 'strategy_s1',
      's2': 'strategy_s2',
      's3': 'strategy_s3',
      'r1': 'risk_management_r1',
      'r2': 'risk_management_r2',
      'r3': 'risk_management_r3',
      'm1': 'metrics_targets_m1',
      'm2': 'metrics_targets_m2',
      'm3': 'metrics_targets_m3'
    };
    return keyMapping[recommendationType] || '';
  };

  // 기후시나리오 이미지 모달 관련 함수들
  const openImageModal = (src: string, title: string) => {
    setSelectedImage({ src, title });
    setIsImageModalOpen(true);
  };

  const closeImageModal = () => {
    setIsImageModalOpen(false);
    setSelectedImage(null);
  };

  // 기후 데이터 생성 모달 관련 함수들
  const openClimateDataModal = () => {
    setShowClimateDataModal(true);
    setGeneratedClimateData(null);
    // 모달 열 때 행정구역 목록 가져오기
    fetchAdministrativeRegions();
  };

  const closeClimateDataModal = () => {
    setShowClimateDataModal(false);
    setGeneratedClimateData(null);
    // 행정구역 검색 상태 초기화
    setRegionSearchTerm('');
    setShowRegionDropdown(false);
  };

  // 행정구역 목록 가져오기
  const fetchAdministrativeRegions = async () => {
    try {
      const response = await apiClient.get('/api/v1/tcfd/administrative-regions');
      if (response.data && response.data.length > 0) {
        setAdministrativeRegions(response.data);
        setFilteredRegions(response.data);
      }
    } catch (error) {
      console.error('행정구역 목록 가져오기 실패:', error);
    }
  };

  // 행정구역 검색 및 필터링
  const handleRegionSearch = (searchTerm: string) => {
    setRegionSearchTerm(searchTerm);
    
    if (!searchTerm.trim()) {
      setFilteredRegions(administrativeRegions);
      setShowRegionDropdown(false);
      return;
    }

    const filtered = administrativeRegions.filter(region => 
      region.sub_region_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      region.region_name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    setFilteredRegions(filtered);
    setShowRegionDropdown(filtered.length > 0);
  };

  // 행정구역 선택
  const selectRegion = (region: {region_code: string, region_name: string, sub_region_name: string}) => {
    setClimateDataSettings({...climateDataSettings, region: region.sub_region_name});
    setRegionSearchTerm(region.sub_region_name);
    setShowRegionDropdown(false);
  };

  // 행정구역 검색 필드 포커스
  const handleRegionFocus = () => {
    if (regionSearchTerm.trim()) {
      setShowRegionDropdown(true);
    }
  };

  const generateClimateData = async () => {
    setIsGeneratingClimateData(true);
    try {
              console.log('🚀 기후 시나리오 막대그래프 차트 생성 시작');
      console.log('📊 설정:', climateDataSettings);
      console.log('🌐 API 엔드포인트: /api/v1/tcfd/climate-scenarios/chart-image');
      console.log('⏱️ 타임아웃: 30초');
      
      // API 호출하여 그래프 생성 (타임아웃 30초 설정)
      const params: any = {
        scenario_code: climateDataSettings.scenario,
        variable_code: climateDataSettings.variable,
        start_year: climateDataSettings.startYear,
        end_year: climateDataSettings.endYear,
        region: climateDataSettings.region  // 행정구역 파라미터 추가
      };
      
      // 추가 연도가 있으면 파라미터에 추가
      if (climateDataSettings.additionalYears && climateDataSettings.additionalYears.length > 0) {
        params.additional_years = climateDataSettings.additionalYears;
      }
      
      const response = await apiClient.get('/api/v1/tcfd/climate-scenarios/chart-image', {
        params,
        timeout: 30000 // 30초 타임아웃
      });

      console.log('📥 API 응답:', response.data);
      
      // TCFD Service 응답 구조 확인
      if (response.data && response.data.success && response.data.image_data) {
        // base64 이미지 데이터를 data URL로 변환
        const base64Data = response.data.image_data;
        const imageData = `data:image/png;base64,${base64Data}`;
        setGeneratedClimateData(imageData);
        console.log('✅ 막대그래프 차트 생성 성공');
        console.log('📊 생성된 이미지 데이터 길이:', base64Data.length);
        console.log('📊 base64 데이터 시작 부분:', base64Data.substring(0, 50));
        
        // 이미지 로드 테스트
        const testImg = new Image();
        testImg.onload = () => {
          console.log('✅ 이미지 로드 성공:', testImg.width, 'x', testImg.height);
        };
        testImg.onerror = () => {
          console.error('❌ 이미지 로드 실패');
        };
        testImg.src = imageData;
      } else if (response.data && response.data.image_data) {
        // image_data가 직접 있는 경우 (기존 구조)
        const base64Data = response.data.image_data;
        const imageData = `data:image/png;base64,${base64Data}`;
        setGeneratedClimateData(imageData);
        console.log('✅ 막대그래프 차트 생성 성공 (기존 구조)');
        console.log('📊 base64 데이터 시작 부분:', base64Data.substring(0, 50));
      } else {
        console.error('❌ API 응답에 이미지 데이터가 없습니다:', response.data);
        console.error('❌ 응답 구조:', {
          success: response.data?.success,
          hasImageData: !!response.data?.image_data,
          message: response.data?.message,
          fullResponse: response.data
        });
        alert('그래프 생성에 실패했습니다. 응답 데이터를 확인해주세요.');
      }
    } catch (error: any) {
      console.error('❌ 막대그래프 차트 생성 오류:', error);
      console.error('❌ 오류 타입:', error.constructor.name);
      console.error('❌ 오류 메시지:', error.message);
      
      if (error.response) {
        console.error('📥 오류 응답:', error.response.data);
        console.error('📊 오류 상태:', error.response.status);
        console.error('📊 오류 헤더:', error.response.headers);
        
        if (error.response.status === 401) {
          alert('인증이 필요합니다. 다시 로그인해주세요.');
        } else if (error.response.status === 503) {
          alert('TCFD Service를 찾을 수 없습니다. 서비스 상태를 확인해주세요.');
        } else if (error.response.status === 500) {
          alert(`서버 내부 오류가 발생했습니다. (${error.response.status})\n${error.response.data?.detail || '알 수 없는 오류'}`);
        } else {
          alert(`그래프 생성 중 오류가 발생했습니다. (${error.response.status})\n${error.response.data?.detail || '알 수 없는 오류'}`);
        }
      } else if (error.request) {
        console.error('📡 네트워크 오류:', error.request);
        console.error('📡 요청 타임아웃:', error.code);
        alert('네트워크 연결을 확인해주세요. 요청이 타임아웃되었을 수 있습니다.');
      } else {
        console.error('❌ 기타 오류:', error);
        alert('그래프 생성 중 예상치 못한 오류가 발생했습니다.');
      }
    } finally {
      setIsGeneratingClimateData(false);
    }
  };

  const downloadGeneratedClimateData = () => {
    if (generatedClimateData) {
      try {
        console.log('💾 테이블 이미지 다운로드 시작');
        
        // base64 데이터를 Blob으로 변환
        const base64Data = generatedClimateData.split(',')[1];
        const byteCharacters = atob(base64Data);
        const byteNumbers = new Array(byteCharacters.length);
        
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'image/png' });
        
        // 다운로드 링크 생성
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        
        // 파일명 생성 (한글 변수명 포함)
        const variableNames: { [key: string]: string } = {
          'HW33': '폭염일수',
          'RN': '연강수량',
          'TA': '연평균기온',
          'TR25': '열대야일수',
          'RAIN80': '호우일수'
        };
        
        const scenarioNames: { [key: string]: string } = {
          'SSP126': 'SSP1-2.6_저탄소',
          'SSP585': 'SSP5-8.5_고탄소'
        };
        
        const variableName = variableNames[climateDataSettings.variable] || climateDataSettings.variable;
        const scenarioName = scenarioNames[climateDataSettings.scenario] || climateDataSettings.scenario;
        
        const filename = `${scenarioName}_${variableName}_${climateDataSettings.startYear}년_${climateDataSettings.endYear}년.png`;
        link.download = filename;
        
        console.log('📁 다운로드 파일명:', filename);
        
        // 다운로드 실행
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // 메모리 정리
        URL.revokeObjectURL(link.href);
        
        console.log('✅ 테이블 이미지 다운로드 완료');
      } catch (error) {
        console.error('❌ 다운로드 오류:', error);
        alert('이미지 다운로드 중 오류가 발생했습니다.');
      }
    }
  };

  // 회사별 기후시나리오 이미지 가져오기
  const getCompanyClimateImages = (companyName: string, ssp: string, year: string, region?: string) => {
    const images: Array<{
      src: string;
      title: string;
      description: string;
    }> = [];

    // 기후지표별 이미지 정보
    const climateIndicators = [
      { key: '연강수량', title: '연간 강수량 변화', description: '연간 총 강수량의 변화 추세를 보여줍니다' },
      { key: '호우일수', title: '호우일수 변화', description: '폭우 발생 일수의 변화를 보여줍니다' },
      { key: '열대야일수', title: '열대야일수 변화', description: '밤 최저기온 25°C 이상 지속되는 일수를 보여줍니다' },
      { key: '폭염일수', title: '폭염일수 변화', description: '낮 최고기온 33°C 이상 지속되는 일수를 보여줍니다' },
      { key: '연평균기온', title: '연평균기온 변화', description: '연간 평균 기온의 변화 추세를 보여줍니다' }
    ];

    // 회사별 지역 매핑
    const companyRegions: Record<string, string[]> = {
      '한온시스템': ['강남구', '경주시', '평택시', '아산시', '대덕구', '울주군'],
      '현대모비스': ['포항시', '의왕시', '창원시', '진천군', '강남구', '성남시', '경주시', '아산시', '울주군', '달성군'],
      'HL만도': ['화성시', '익산시', '원주시', '성남시', '평택시', '연수구']
    };

    // 회사명 정규화 (대소문자, 공백 제거)
    const normalizedCompanyName = companyName.replace(/\s+/g, '').toLowerCase();
    let regions: string[] = [];
    
    for (const [company, companyRegionsList] of Object.entries(companyRegions)) {
      if (normalizedCompanyName.includes(company.toLowerCase().replace(/\s+/g, ''))) {
        regions = companyRegionsList;
        break;
      }
    }

    if (regions.length === 0) {
      return images;
    }

    // 지역 필터링 적용
    if (region && region !== '전체') {
      regions = regions.filter(r => r === region);
    }

    // 연도별 파일명 패턴
    const yearPattern = year === '2026-2030' ? '_2026_2030' : '';

    // 각 지역과 기후지표에 대해 이미지 생성
    regions.forEach(region => {
      climateIndicators.forEach(indicator => {
        const filename = `${ssp}_${region}_${indicator.key}${yearPattern}.png`;
        const imagePath = `/${companyName}/${filename}`;
        
        images.push({
          src: imagePath,
          title: `${region} ${indicator.title}`,
          description: indicator.description
        });
      });
    });

    return images;
  };

  // 일반 기후시나리오 이미지 가져오기 (SSP126, SSP585)
  const getGeneralClimateImages = (ssp: 'SSP126' | 'SSP585') => {
    const images: Array<{
      src: string;
      title: string;
      description: string;
    }> = [];

    // SSP별 폴더명과 이미지 매핑 (실제 파일명 패턴에 맞춤)
    const sspImageMap = {
      'SSP126': {
        folder: 'image_ssp2.6',
        images: [
          { key: '호우일수', title: '호우일수 변화', description: '폭우 발생 일수의 변화를 보여줍니다' },
          { key: '폭염일수', title: '폭염일수 변화', description: '낮 최고기온 33°C 이상 지속되는 일수를 보여줍니다' },
          { key: '평균_최고기온', title: '평균 최고기온 변화', description: '일평균 최고기온의 변화를 보여줍니다' },
          { key: '최대무강수지속기간', title: '최대 무강수 지속기간', description: '연속으로 비가 오지 않는 최대 기간을 보여줍니다' },
          { key: '열대야일수', title: '열대야일수 변화', description: '밤 최저기온 25°C 이상 지속되는 일수를 보여줍니다' },
          { key: '연평균기온', title: '연평균기온 변화', description: '연간 평균 기온의 변화 추세를 보여줍니다' },
          { key: '강수량', title: '강수량 변화', description: '총 강수량의 변화를 보여줍니다' },
          { key: '강수강도', title: '강수강도 변화', description: '강수의 세기를 보여줍니다' },
          { key: '1일_한파일수', title: '1일 한파일수', description: '하루 중 한파가 지속되는 시간을 보여줍니다' },
          { key: '1일_최대강수량', title: '1일 최대강수량', description: '하루 중 최대 강수량을 보여줍니다' }
        ]
      },
      'SSP585': {
        folder: 'image_ssp8.5',
        images: [
          { key: '호우일수', title: '호우일수 변화', description: '폭우 발생 일수의 변화를 보여줍니다' },
          { key: '폭염_일수', title: '폭염일수 변화', description: '낮 최고기온 33°C 이상 지속되는 일수를 보여줍니다' },
          { key: '평균_최고기온', title: '평균 최고기온 변화', description: '일평균 최고기온의 변화를 보여줍니다' },
          { key: '최대무강수지속기간', title: '최대 무강수 지속기간', description: '연속으로 비가 오지 않는 최대 기간을 보여줍니다' },
          { key: '열대야일수', title: '열대야일수 변화', description: '밤 최저기온 25°C 이상 지속되는 일수를 보여줍니다' },
          { key: '연평균기온', title: '연평균기온 변화', description: '연간 평균 기온의 변화 추세를 보여줍니다' },
          { key: '강수량', title: '강수량 변화', description: '총 강수량의 변화를 보여줍니다' },
          { key: '강수강도', title: '강수강도 변화', description: '강수의 세기를 보여줍니다' },
          { key: '한파일수', title: '한파일수', description: '한파가 지속되는 일수를 보여줍니다' },
          { key: '1일_최대강수량', title: '1일 최대강수량', description: '하루 중 최대 강수량을 보여줍니다' }
        ]
      }
    };

    const sspData = sspImageMap[ssp];
    if (!sspData) return images;

    // 각 기후지표에 대해 이미지 생성 (실제 파일명 패턴에 맞춤)
    sspData.images.forEach(indicator => {
      // 파일명 패턴에 따라 이미지 생성
      if (indicator.key === '호우일수' || indicator.key === '폭염_일수' || indicator.key === '폭염일수') {
        // 호우일수, 폭염일수는 1, 2번 이미지가 있음
        for (let i = 1; i <= 2; i++) {
          // 실제 파일명 패턴: SSP_585_폭염_일수_1.png
          const filename = `SSP_${ssp === 'SSP126' ? '126' : '585'}_${indicator.key}_${i}.png`;
          const imagePath = `/${sspData.folder}/${filename}`;
          
          images.push({
            src: imagePath,
            title: `${indicator.title} ${i}`,
            description: `${indicator.description} (${ssp} 시나리오)`
          });
        }
      } else if (indicator.key === '열대야일수') {
        // 열대야일수는 1, 2번 이미지가 있음
        for (let i = 1; i <= 2; i++) {
          const filename = `SSP_${ssp === 'SSP126' ? '126' : '585'}_${indicator.key}_${i}.png`;
          const imagePath = `/${sspData.folder}/${filename}`;
          
          images.push({
            src: imagePath,
            title: `${indicator.title} ${i}`,
            description: `${indicator.description} (${ssp} 시나리오)`
          });
        }
      } else {
        // 나머지는 단일 이미지 (특별한 경우 처리)
        let filename: string;
        
        // SSP126의 경우 특별한 파일명 패턴 처리
        if (ssp === 'SSP126' && indicator.key === '1일_최대강수량') {
          filename = `SSP_126_1일_최대강수량_1.png`;
        } else {
          filename = `SSP_${ssp === 'SSP126' ? '126' : '585'}_${indicator.key}.png`;
        }
        
        const imagePath = `/${sspData.folder}/${filename}`;
        
        images.push({
          src: imagePath,
          title: indicator.title,
          description: `${indicator.description} (${ssp} 시나리오)`
        });
      }
    });

    return images;
  };

  // 카테고리별로 이미지 필터링하는 함수
  const getFilteredGeneralClimateImages = (ssp: 'SSP126' | 'SSP585', category: string) => {
    const allImages = getGeneralClimateImages(ssp);
    
    if (category === 'all') {
      return allImages;
    }
    
    const categoryMap = {
      'temperature': ['연평균기온', '평균_최고기온', '열대야일수', '폭염일수', '폭염_일수', '한파일수', '1일_한파일수'],
      'precipitation': ['강수량', '강수강도', '호우일수', '1일_최대강수량', '1일_최대강수량_1'],
      'extreme': ['최대무강수지속기간', '폭염일수', '폭염_일수', '호우일수', '한파일수', '1일_한파일수']
    };
    
    const targetKeys = categoryMap[category as keyof typeof categoryMap] || [];
    
    return allImages.filter(image => {
      return targetKeys.some(key => image.title.includes(key) || image.description.includes(key));
    });
  };

  // 다운로드 함수들
  const downloadReportAsText = (content: string, filename: string) => {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadReportAsWord = async (content: string, filename: string) => {
    try {
      const downloadContent: DownloadContent = {
        title: 'TCFD 보고서',
        draft: content,
        polished: content,
        companyName: companyFinancialData?.company_name || 'Unknown',
        timestamp: new Date().toISOString()
      };
      
      await downloadAsWordFromServer(downloadContent);
    } catch (error) {
      console.error('Word 다운로드 실패:', error);
      alert('Word 다운로드에 실패했습니다.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <div className="pt-16">
                 <div className="max-w-[95%] mx-auto px-2 sm:px-4 lg:px-6 py-section">
          {/* 헤더 */}
          <div className="text-center mb-8">
                                           <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-brand shadow-soft p-8 max-w-7xl mx-auto relative">
                 <div className="flex justify-between items-start">
                   <div className="flex-1">
                     <h1 className="text-3xl font-bold text-primary-600 mb-3">TCFD ESG SR 작성</h1>
                     <p className="text-gray-700 text-lg">TCFD(Task Force on Climate-related Financial Disclosures)<br/>
                   기업이 기후변화로 인한 위험과 기회를 어떻게 관리하고 있는지 투명하게 공시하도록 권고합니다.<br/>
                   핵심은 거버넌스, 전략, 리스크 관리, 지표 및 목표의 4가지 영역에서 기후 관련 정보를 보고하는 것입니다.<br/>
                   투자자·금융기관 등이 기후 리스크를 평가하고 의사결정에 반영할 수 있는 국제 표준 프레임워크 역할을 합니다.</p>
                     {userCompanyName && (
                       <p className="text-primary-600 font-semibold mt-3">
                         🏢 접근 가능한 회사: {userCompanyName}
                       </p>
                     )}
                     
                     {/* TCFD 알아보기 버튼 추가 */}
                     <div className="mt-4">
                       <button
                         onClick={() => window.open('https://www.fsb-tcfd.org/', '_blank')}
                         className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 shadow-sm hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                       >
                         <span className="mr-2">🌐</span>
                         TCFD 알아보기
                         <span className="ml-2">→</span>
                       </button>
                     </div>
                   </div>
                                       <button
                      onClick={() => setIsGuideOpen(true)}
                      className="ml-6 p-3 bg-blue-100 hover:bg-blue-200 border border-blue-300 rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                      title="이용가이드 보기"
                    >
                      <div className="w-6 h-6 bg-blue-600 text-white rounded flex items-center justify-center text-sm font-bold">
                        !
                      </div>
                    </button>
                 </div>
               </div>
          </div>

          {/* 탭 네비게이션과 컨텐츠를 가로로 배치 */}
                     <div className="flex gap-8">
            {/* 왼쪽 세로 탭 네비게이션 */}
                         <div className="w-72 bg-white rounded-brand shadow-soft border border-gray-300 p-4">
              <nav className="space-y-2" aria-label="Tabs">
                {[
                  { id: 0, name: '프로젝트요약', icon: '📋' },
                  { id: 1, name: '회사정보', icon: '🏢' },
                  { id: 2, name: '재무정보', icon: '💰' },
                  { id: 3, name: 'TCFD 프레임워크', icon: '📊' },
                  { id: 4, name: '기후시나리오', icon: '🌍' },
                  { id: 5, name: 'AI보고서 초안', icon: '🤖', subtitle: 'OpenAI + KoAlpaca' },
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left py-3 px-4 rounded-lg font-medium text-sm transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-100 text-primary-700 border-l-4 border-primary-600'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-primary-600'
                    }`}
                  >
                    <div className="flex items-center">
                      <span className="mr-3">{tab.icon}</span>
                      <div className="text-left">
                        <div>{tab.name}</div>
                        {tab.subtitle && (
                          <div className="text-xs text-gray-500 mt-1 font-normal">
                            {tab.subtitle}
                          </div>
                        )}
                      </div>
                    </div>
                  </button>
                ))}
              </nav>
          </div>

            {/* 오른쪽 탭 컨텐츠 */}
                         <div className="flex-1 bg-white rounded-brand shadow-soft border border-gray-300 p-8">
            {/* 탭 0: 프로젝트요약 */}
            {activeTab === 0 && (
              <ProjectSummaryTab />
            )}

            {/* 탭 1: 회사정보 */}
            {activeTab === 1 && (
                <div className="space-y-6">
                                     <div className="flex items-center gap-3 mb-6">
                     <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                       <span className="text-lg font-bold text-primary-600">🏢</span>
                     </div>
                     <h2 className="text-xl font-semibold text-gray-800">회사정보</h2>
                   </div>

                {/* 회사 검색 */}
                  <div className="space-y-4">
                    <label className="block text-sm font-medium text-gray-700">
                        회사명 검색
                      </label>
                    {userCompanyName && (
                      <div className="bg-blue-50 border border-blue-200 rounded-brand p-3">
                        <p className="text-blue-700 text-sm">
                          ℹ️ 회원가입 시 입력한 회사이름 &ldquo;{userCompanyName}&rdquo;만 검색 가능합니다.
                        </p>
                      </div>
                    )}
                    <div className="flex gap-3">
                      <input
                        type="text"
                        value={companyName}
                        onChange={(e) => setCompanyName(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && loadCompanyFinancialData(companyName)}
                        placeholder={userCompanyName ? `검색할 회사명: ${userCompanyName}` : "회사명을 입력하세요"}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-brand focus:ring-2 focus:ring-primary-500 focus:border-transparent text-black placeholder-gray-500"
                      />
                    <button
                        onClick={() => loadCompanyFinancialData(companyName)}
                        disabled={isLoadingCompany || !companyName.trim()}
                        className="px-6 py-2 bg-primary-600 text-white rounded-brand shadow-soft hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isLoadingCompany ? '검색 중...' : '검색'}
                    </button>
                    </div>
                  </div>

                  {/* 검색 결과 */}
                  {companyError && (
                    <div className="bg-red-50 border border-red-200 rounded-brand p-4">
                      <p className="text-red-700">{companyError}</p>
                </div>
                  )}

                  {/* 기업개요 정보 표시 */}
                  {companyOverview && (
                    <div className="bg-success-50 border border-success-200 rounded-brand p-6">
                                             <h3 className="text-lg font-semibold text-black mb-4">
                         ✅ {companyOverview.종목명}
                      </h3>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-3">
                                                     <div>
                             <span className="font-medium text-gray-700">종목코드:</span>
                             <span className="ml-2 text-gray-900">{companyOverview.종목코드?.toString().padStart(6, '0')}</span>
                           </div>
                          <div>
                            <span className="font-medium text-gray-700">설립일:</span>
                            <span className="ml-2 text-gray-900">{companyOverview.설립일 || '정보 없음'}</span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">대표자:</span>
                            <span className="ml-2 text-gray-900">{companyOverview.대표자 || '정보 없음'}</span>
                          </div>
                    </div>

                        <div className="space-y-3">
                          <div>
                            <span className="font-medium text-gray-700">주소:</span>
                            <span className="ml-2 text-gray-900">{companyOverview.주소 || '정보 없음'}</span>
                  </div>
                          <div>
                            <span className="font-medium text-gray-700">전화번호:</span>
                            <span className="ml-2 text-gray-900">{companyOverview.전화번호 || '정보 없음'}</span>
                          </div>
                          <div>
                            <span className="font-medium text-gray-700">홈페이지:</span>
                            <span className="ml-2 text-gray-900">
                              {companyOverview.홈페이지 ? (
                                <a href={companyOverview.홈페이지} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                  {companyOverview.홈페이지}
                                </a>
                              ) : (
                                '정보 없음'
                              )}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="mt-6 text-center">
                        <p className="text-black mb-4">
                          기업개요 정보가 성공적으로 검색되었습니다. 재무정보 탭에서 상세한 재무 데이터를 확인하세요.
                        </p>
                        <button
                          onClick={() => setActiveTab(2)}
                          className="px-6 py-2 bg-success-600 text-black rounded-brand shadow-soft hover:bg-success-700 transition-colors focus:outline-none focus:ring-2 focus:ring-success-100"
                        >
                          재무정보 탭으로 이동
                        </button>
                      </div>
                    </div>
                  )}

                  {/* 기존 성공 메시지 (기업개요 정보가 없을 때만 표시) */}
                  {companyFinancialData && !companyOverview && (
                    <div className="bg-success-50 border border-success-200 rounded-brand p-6 text-center">
                      <h3 className="text-lg font-semibold text-black mb-2">
                        ✅ {companyFinancialData.company_name} 검색 완료
                      </h3>
                      <p className="text-black mb-4">
                        회사 정보가 성공적으로 검색되었습니다. 재무정보 탭에서 상세한 재무 데이터를 확인하세요.
                      </p>
                      <button
                        onClick={() => setActiveTab(2)}
                        className="px-6 py-2 bg-success-600 text-black rounded-brand shadow-soft hover:bg-success-700 transition-colors focus:outline-none focus:ring-2 focus:ring-success-100"
                      >
                        재무정보 탭으로 이동
                      </button>
                  </div>
                )}
              </div>
            )}

            {/* 탭 2: 재무정보 */}
            {activeTab === 2 && (
              <div>
                <h2 className="text-2xl font-bold text-primary-600 mb-6">💰 재무정보</h2>

                {/* 회사 검색 결과가 없을 때 안내 메시지 */}
                {!companyFinancialData && (
                  <div className="text-center py-12">
                    <div className="bg-primary-100 border border-primary-300 rounded-brand p-6">
                        <h3 className="text-lg font-semibold text-primary-700 mb-2">회사 검색이 필요합니다</h3>
                      <p className="text-primary-600 mb-4">
                        회사정보 탭에서 회사명을 검색하면 해당 회사의 재무정보가 여기에 표시됩니다.
                      </p>
                      <button
                        onClick={() => setActiveTab(1)}
                        className="px-6 py-2 bg-primary-600 text-white rounded-brand shadow-soft hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-100"
                      >
                        회사정보 탭으로 이동
                      </button>
                    </div>
                  </div>
                )}

                {/* 회사별 재무정보 표시 */}
                {companyFinancialData && (
                  <div>
                    {/* 5개 테이블 데이터 표시 - 순서 변경 */}
                      {renderFinancialTable(
                        companyFinancialData.data?.corporation,
                        '기업 정보',
                      )}
                    {renderFinancialTable(companyFinancialData.data?.financial, '재무상태')}
                    {renderFinancialTable(companyFinancialData.data?.profit, '손익계산')}
                    {renderFinancialTable(companyFinancialData.data?.executive, '임원 정보')}
                    {renderFinancialTable(companyFinancialData.data?.employee, '직원 정보')}
                  </div>
                )}
              </div>
            )}

            {/* 탭 3: TCFD 프레임워크 */}
            {activeTab === 3 && (
              <div>
                <h2 className="text-2xl font-bold text-primary-600 mb-6">📊 TCFD 프레임워크</h2>

                {/* TCFD 표준 정보 표시 */}
                <div className="mb-8">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">TCFD 표준 권고사항</h3>

                  {isLoadingTcfd && (
                    <div className="text-center py-8">
                      <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
                      <p className="mt-2 text-gray-700">TCFD 표준 정보를 불러오는 중...</p>
                    </div>
                  )}

                  {tcfdError && (
                    <div className="bg-danger-50 border border-danger-200 rounded-brand p-4 mb-4">
                      <p className="text-danger-700">{tcfdError}</p>
                    </div>
                  )}

                    {!isLoadingTcfd && !tcfdError && Object.keys(tcfdStandards).length > 0 && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {Object.entries(tcfdStandards).map(([category, data]) => (
                          <div key={category} className={`${data.bgColor} p-6 rounded-brand shadow-soft`}>
                            <h4 className={`text-xl font-semibold mb-3 ${data.color}`}>{data.title}</h4>
                            <p className={`mb-4 ${data.color}`}>{data.description}</p>

                            {/* 해당 카테고리의 공개 정보 미리보기 */}
                            {data.disclosures.length > 0 && (
                              <div className="space-y-3">
                                <h5 className="font-medium text-gray-800 mb-2">
                                  공개 요구사항 ({data.disclosures.length}개):
                                </h5>
                                {/* 첫 번째 항목만 미리보기로 표시 */}
                                <div className="bg-white p-3 rounded-brand shadow-soft border border-gray-300">
                                  <h6 className="font-semibold text-gray-800 mb-1">
                                    {data.disclosures[0].disclosure_id}
                                  </h6>
                                  <p className="text-sm text-gray-700 mb-1">
                                    {data.disclosures[0].disclosure_summary}
                                  </p>
                                  <p className="text-xs text-gray-500">
                                    {data.disclosures[0].disclosure_detail}
                                  </p>
                                </div>

                                {/* 더 많은 항목이 있을 경우 상세보기 버튼 표시 */}
                                {data.disclosures.length > 1 && (
                                  <div className="text-center pt-2">
                                    <button
                                      onClick={() => handleTcfdDetails(category, data)}
                                      className={`${data.color
                                        .replace('text-', 'bg-')
                                        .replace('-700', '-600')} px-4 py-2 text-black rounded-brand shadow-soft hover:opacity-90 transition-colors text-sm font-medium border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-100`}
                                    >
                                      상세보기 ({data.disclosures.length}개 전체)
                                    </button>
                                  </div>
                                )}
                              </div>
                            )}

                            {data.disclosures.length === 0 && (
                              <p className="text-gray-500 text-sm">해당 카테고리의 공개 정보가 없습니다.</p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}

                  {!isLoadingTcfd && !tcfdError && Object.keys(tcfdStandards).length === 0 && (
                    <div className="text-center py-8">
                      <p className="text-gray-500">TCFD 표준 정보가 없습니다.</p>
                    </div>
                  )}
                </div>

                {/* TCFD 11개 인덱스 입력 폼 */}
                {companyFinancialData && (
                  <div className="mt-8">
                    <h4 className="text-lg font-semibold text-gray-800 mb-4">
                      TCFD 11개 핵심 인덱스 데이터 입력
                    </h4>

                    {/* 거버넌스 */}
                    <div className="mb-6">
                      <h5 className="text-md font-semibold text-blue-700 mb-3 border-b border-blue-200 pb-2">
                        거버넌스 (Governance)
                      </h5>
                      <div className="space-y-4">
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            G1: 기후 관련 위험과 기회에 대한 이사회 감독
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="이사회가 기후 관련 위험과 기회를 어떻게 감독하고 있는지 설명하세요..."
                            value={tcfdInputData.governance_g1}
                            onChange={(e) => handleTcfdInputChange('governance_g1', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <p className="text-xs text-blue-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;이사회는 기후변화 관련 주요 리스크와 기회를 정기적으로 검토하며, 연 2회 이상 ESG
                              위원회를 통해 관련 안건을 심의합니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('g1', 'openai')}
                              className="px-3 py-2 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('g1', 'koalpaca')}
                              className="px-3 py-2 bg-purple-600 text-white text-xs rounded-lg hover:bg-purple-700 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                          </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            G2: 기후 관련 위험과 기회에 대한 경영진 역할
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="경영진이 기후 관련 위험과 기회를 어떻게 관리하는지 설명하세요..."
                            value={tcfdInputData.governance_g2}
                            onChange={(e) => handleTcfdInputChange('governance_g2', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <p className="text-xs text-blue-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;경영진은 탄소중립 목표 달성을 위한 실행계획을 수립하고, 각 사업부에 KPI를 배분하여
                              이행 상황을 모니터링합니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('g2', 'openai')}
                              className="px-3 py-2 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('g2', 'koalpaca')}
                              className="px-3 py-2 bg-purple-600 text-white text-xs rounded-lg hover:bg-purple-700 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                        </div>
                        </div>

                      </div>
                    </div>

                    {/* 전략 */}
                    <div className="mb-6">
                      <h5 className="text-md font-semibold text-green-700 mb-3 border-b border-green-200 pb-2">
                        전략 (Strategy)
                      </h5>
                      <div className="space-y-4">
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            S1: 기후 관련 위험과 기회의 비즈니스 영향
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="기후 관련 위험과 기회가 조직의 비즈니스, 전략, 재무 계획에 미치는 영향을 설명하세요..."
                            value={tcfdInputData.strategy_s1}
                            onChange={(e) => handleTcfdInputChange('strategy_s1', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                            <p className="text-xs text-green-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;기후변화로 인한 원자재 가격 변동은 당사 제조원가에 영향을 미칠 수 있으며, 이에 따라
                              공급망 다변화 전략을 추진하고 있습니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('s1', 'openai')}
                              className="px-3 py-2 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('s1', 'koalpaca')}
                              className="px-3 py-2 bg-purple-600 text-white text-xs rounded-lg hover:bg-purple-700 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                          </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            S2: 전략적 영향의 실제 잠재적 영향
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="조직의 전략, 비즈니스, 재무 계획에 미치는 기후 관련 위험과 기회의 실제 잠재적 영향을 설명하세요..."
                            value={tcfdInputData.strategy_s2}
                            onChange={(e) => handleTcfdInputChange('strategy_s2', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                            <p className="text-xs text-green-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;탄소중립 정책으로 인한 규제 강화는 당사 제품의 경쟁력을 재정의할 수 있으며, 친환경
                              기술 개발에 대한 투자를 확대하고 있습니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('s2', 'openai')}
                              className="px-3 py-2 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('s2', 'koalpaca')}
                              className="px-3 py-2 bg-purple-600 text-white text-xs rounded-lg hover:bg-purple-700 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                          </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            S3: 기후 시나리오 분석
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="조직이 사용하는 기후 시나리오 분석 방법과 결과를 설명하세요..."
                            value={tcfdInputData.strategy_s3}
                            onChange={(e) => handleTcfdInputChange('strategy_s3', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                            <p className="text-xs text-green-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;IPCC RCP 2.6 및 RCP 8.5 시나리오를 기반으로 2030년, 2050년, 2100년까지의 기후 변화
                              영향을 분석하여 장기 전략을 수립하고 있습니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('s3', 'openai')}
                              className="px-3 py-2 bg-blue-600 text-white text-xs rounded-lg hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('s3', 'koalpaca')}
                              className="px-3 py-2 bg-purple-600 text-white text-xs rounded-lg hover:bg-purple-700 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* 리스크 관리 */}
                    <div className="mb-6">
                      <h5 className="text-md font-semibold text-yellow-700 mb-3 border-b border-yellow-200 pb-2">
                        리스크 관리 (Risk Management)
                      </h5>
                      <div className="space-y-4">
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            R1: 기후 관련 위험 식별 및 평가 프로세스
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="조직이 기후 관련 위험을 식별, 평가, 관리하는 프로세스를 설명하세요..."
                            value={tcfdInputData.risk_management_r1}
                            onChange={(e) => handleTcfdInputChange('risk_management_r1', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <p className="text-xs text-yellow-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;기후 관련 위험은 분기별 리스크 평가 회의에서 식별하고, 위험도와 영향도를 매트릭스로
                              평가하여 우선순위를 정하고 있습니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('r1', 'openai')}
                              className="px-3 py-2 bg-yellow-600 text-white text-xs rounded-lg hover:bg-yellow-700 transition-colors focus:outline-none focus:ring-2 focus:ring-yellow-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('r1', 'koalpaca')}
                              className="px-3 py-2 bg-orange-600 text-white text-xs rounded-lg hover:bg-orange-700 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                          </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            R2: 리스크 관리 프로세스 통합
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="조직의 전반적인 리스크 관리 프로세스에 기후 관련 위험을 통합하는 방법을 설명하세요..."
                            value={tcfdInputData.risk_management_r2}
                            onChange={(e) => handleTcfdInputChange('risk_management_r2', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <p className="text-xs text-yellow-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;기후 관련 위험은 기존 ERM(Enterprise Risk Management) 프레임워크에 통합하여 전사적
                              리스크 관리 체계의 일부로 운영하고 있습니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('r2', 'openai')}
                              className="px-3 py-2 bg-yellow-600 text-white text-xs rounded-lg hover:bg-yellow-700 transition-colors focus:outline-none focus:ring-2 focus:ring-yellow-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('r2', 'koalpaca')}
                              className="px-3 py-2 bg-orange-600 text-white text-xs rounded-lg hover:bg-orange-700 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                          </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            R3: 기후 관련 위험을 전사적 리스크 관리 프로세스에 통합
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="기후 관련 위험을 조직의 전사적 리스크 관리 프로세스에 어떻게 통합하고 있는지 설명하세요..."
                            value={tcfdInputData.risk_management_r3}
                            onChange={(e) => handleTcfdInputChange('risk_management_r3', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <p className="text-xs text-yellow-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;기후 관련 위험은 분기별 전사적 위험 평가에 포함되어 있으며, 위험도와 영향도를
                              정량적으로 평가하여 리스크 매트릭스에 반영하고 있습니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('r3', 'openai')}
                              className="px-3 py-2 bg-yellow-600 text-white text-xs rounded-lg hover:bg-yellow-700 transition-colors focus:outline-none focus:ring-2 focus:ring-yellow-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('r3', 'koalpaca')}
                              className="px-3 py-2 bg-orange-600 text-white text-xs rounded-lg hover:bg-orange-700 transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* 지표 및 목표 */}
                    <div className="mb-6">
                      <h5 className="text-md font-semibold text-purple-700 mb-3 border-b border-purple-200 pb-2">
                        지표 및 목표 (Metrics and Targets)
                      </h5>
                      <div className="space-y-4">
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            M1: 기후 관련 위험 평가 지표
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="조직이 기후 관련 위험과 기회를 평가하는 데 사용하는 지표를 설명하세요..."
                            value={tcfdInputData.metrics_targets_m1}
                            onChange={(e) => handleTcfdInputChange('metrics_targets_m1', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                            <p className="text-xs text-purple-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;탄소 배출량(tCO2e), 에너지 효율성(단위당 에너지 소비량), 기후 관련 규제 준수율 등을
                              주요 지표로 사용하고 있습니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('m1', 'openai')}
                              className="px-3 py-2 bg-purple-600 text-white text-xs rounded-lg hover:bg-purple-700 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('m1', 'koalpaca')}
                              className="px-3 py-2 bg-pink-600 text-white text-xs rounded-lg hover:bg-pink-700 transition-colors focus:outline-none focus:ring-2 focus:ring-pink-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                          </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            M2: 기후 관련 기회 평가 지표
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="기후 관련 위험과 기회를 평가하는 데 사용하는 지표를 설명하세요..."
                            value={tcfdInputData.metrics_targets_m2}
                            onChange={(e) => handleTcfdInputChange('metrics_targets_m2', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                            <p className="text-xs text-purple-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;친환경 제품 매출 비중, 재생에너지 사용률, 기후 관련 R&amp;D 투자 비율 등을 기회 평가
                              지표로 활용하고 있습니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('m2', 'openai')}
                              className="px-3 py-2 bg-purple-600 text-white text-xs rounded-lg hover:bg-purple-700 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('m2', 'koalpaca')}
                              className="px-3 py-2 bg-pink-600 text-white text-xs rounded-lg hover:bg-pink-700 transition-colors focus:outline-none focus:ring-2 focus:ring-pink-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                          </div>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            M3: 기후 관련 목표 설정
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="조직이 기후 관련 위험과 기회를 평가하는 데 사용하는 목표를 설명하세요..."
                            value={tcfdInputData.metrics_targets_m3}
                            onChange={(e) => handleTcfdInputChange('metrics_targets_m3', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                            <p className="text-xs text-purple-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;2030년까지 탄소 배출량 30% 감축, 2050년까지 탄소중립 달성, 재생에너지 사용률 50% 달성
                              등의 목표를 설정하고 있습니다.&rdquo;
                            </p>
                          </div>
                          {/* AI 문장 생성 버튼 */}
                          <div className="mt-3 flex gap-2">
                            <button
                              onClick={() => handleGenerateRecommendation('m3', 'openai')}
                              className="px-3 py-2 bg-purple-600 text-white text-xs rounded-lg hover:bg-purple-700 transition-colors focus:outline-none focus:ring-2 focus:ring-purple-500"
                            >
                              🤖 OpenAI로 문장 생성
                            </button>
                            <button
                              onClick={() => handleGenerateRecommendation('m3', 'koalpaca')}
                              className="px-3 py-2 bg-pink-600 text-white text-xs rounded-lg hover:bg-pink-700 transition-colors focus:outline-none focus:ring-2 focus:ring-pink-500"
                            >
                              🚀 KoAlpaca로 문장 생성
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* 제출 버튼 */}
                    <div className="flex justify-center mt-8">
                      <button
                        className="px-6 py-3 bg-primary-600 text-white rounded-brand shadow-soft hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-100 disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
                        onClick={handleTcfdSubmit}
                        disabled={isSubmitting}
                      >
                        {isSubmitting ? '저장 중...' : 'TCFD 분석 시작'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 탭 4: 기후시나리오 */}
            {activeTab === 4 && (
              <div>
                <h2 className="text-2xl font-bold text-primary-600 mb-6">🌍 기후시나리오</h2>
                
                {/* 기후 데이터 생성 버튼 추가 */}
                <div className="mb-6 text-center">
                  <button
                    onClick={openClimateDataModal}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 mx-auto"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    <span>기후 데이터 생성</span>
                  </button>
                </div>
                
                {/* 회사 검색이 완료되지 않은 경우 기본 안내 */}
                {!companyOverview && (
                  <div className="space-y-6">
                    {/* SSP 시나리오별 탭 */}
                    <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
                    <button
                        onClick={() => setSelectedSSP('SSP126')}
                        className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                          selectedSSP === 'SSP126'
                            ? 'bg-white text-blue-600 shadow-sm'
                            : 'text-gray-600 hover:text-gray-800'
                        }`}
                      >
                        SSP 1-2.6 (저탄소)
                      </button>
                      <button
                        onClick={() => setSelectedSSP('SSP585')}
                        className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                          selectedSSP === 'SSP585'
                            ? 'bg-white text-blue-600 shadow-sm'
                            : 'text-gray-600 hover:text-gray-800'
                        }`}
                      >
                        SSP 5-8.5 (고탄소)
                    </button>
                  </div>

                    {/* 기후지표 카테고리별 탭 */}
                    <div className="flex flex-wrap gap-2 mb-6">
                    <button
                        onClick={() => setSelectedCategory('all')}
                        className={`px-4 py-2 rounded-md font-medium transition-colors ${
                          selectedCategory === 'all'
                            ? 'bg-blue-600 text-white shadow-sm'
                            : 'bg-gray-200 text-gray-600 hover:text-gray-800'
                        }`}
                      >
                        전체
                      </button>
                      <button
                        onClick={() => setSelectedCategory('temperature')}
                        className={`px-4 py-2 rounded-md font-medium transition-colors ${
                          selectedCategory === 'temperature'
                            ? 'bg-blue-600 text-white shadow-sm'
                            : 'bg-gray-200 text-gray-600 hover:text-gray-800'
                        }`}
                      >
                        온도 관련
                      </button>
                      <button
                        onClick={() => setSelectedCategory('precipitation')}
                        className={`px-4 py-2 rounded-md font-medium transition-colors ${
                          selectedCategory === 'precipitation'
                            ? 'bg-blue-600 text-white shadow-sm'
                            : 'bg-gray-200 text-gray-600 hover:text-gray-800'
                        }`}
                      >
                        강수 관련
                      </button>
                      <button
                        onClick={() => setSelectedCategory('extreme')}
                        className={`px-4 py-2 rounded-md font-medium transition-colors ${
                          selectedCategory === 'extreme'
                            ? 'bg-blue-600 text-white shadow-sm'
                            : 'bg-gray-200 text-gray-600 hover:text-gray-800'
                        }`}
                      >
                        극한 현상
                    </button>
                  </div>

                    {/* SSP 126 (저탄소) 시나리오 설명 */}
                    {selectedSSP === 'SSP126' && (
                      <div className="bg-info-50 p-6 rounded-brand border border-info-200">
                        <h3 className="text-xl font-semibold text-info-800 mb-3">SSP 1-2.6 (극저탄소 시나리오)</h3>
                        <p className="text-info-700 mb-4 text-lg">2100년까지 1.6°C 온도 상승, 파리협정 목표 달성</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                          {getFilteredGeneralClimateImages('SSP126', selectedCategory).map((image, index) => (
                            <div key={index} className="bg-white rounded-lg border border-info-200 shadow-sm overflow-hidden">
                              <div className="p-4">
                                <h5 className="font-semibold text-gray-800 mb-2">{image.title}</h5>
                                <p className="text-sm text-gray-600 mb-3">{image.description}</p>
                                <div className="relative aspect-video bg-gray-100 rounded-md overflow-hidden">
                                  <img
                                    src={image.src}
                                    alt={image.title}
                                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-200 cursor-pointer"
                                    onClick={() => openImageModal(image.src, image.title)}
                                  />
                                  {/* 다운로드 버튼 */}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      downloadImage(image.src, image.title);
                                    }}
                                    className="absolute top-2 right-2 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors shadow-lg"
                                    title="이미지 다운로드"
                                  >
                                    <span className="text-sm">⬇️</span>
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* SSP 585 (고탄소) 시나리오 설명 */}
                    {selectedSSP === 'SSP585' && (
                      <div className="bg-danger-50 p-6 rounded-brand border border-danger-200">
                        <h3 className="text-xl font-semibold text-danger-800 mb-3">SSP 5-8.5 (고탄소 시나리오)</h3>
                        <p className="text-danger-700 mb-4 text-lg">2100년까지 4.9°C 온도 상승, 극단적인 기후 변화</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                          {getFilteredGeneralClimateImages('SSP585', selectedCategory).map((image, index) => (
                            <div key={index} className="bg-white rounded-lg border border-danger-200 shadow-sm overflow-hidden">
                              <div className="p-4">
                                <h5 className="font-semibold text-gray-800 mb-2">{image.title}</h5>
                                <p className="text-sm text-gray-600 mb-3">{image.description}</p>
                                <div className="relative aspect-video bg-gray-100 rounded-md overflow-hidden">
                                  <img
                                    src={image.src}
                                    alt={image.title}
                                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-200 cursor-pointer"
                                    onClick={() => openImageModal(image.src, image.title)}
                                  />
                                  {/* 다운로드 버튼 */}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      downloadImage(image.src, image.title);
                                    }}
                                    className="absolute top-2 right-2 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors shadow-lg"
                                    title="이미지 다운로드"
                                  >
                                    <span className="text-sm">⬇️</span>
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                  {/* 기후 시나리오 이미지 갤러리로 이동하는 More 버튼 */}
                    <div className="mt-8 text-center">
                    <button
                      onClick={() => {
                        const token = localStorage.getItem('auth_token');
                        if (token) {
                          router.push('/climate-scenarios');
                        } else {
                          alert('로그인이 필요합니다. 먼저 로그인해주세요.');
                          router.push('/login');
                        }
                      }}
                        className="px-8 py-3 bg-success-600 text-black rounded-brand shadow-soft hover:bg-success-700 transition-colors font-medium text-lg focus:outline-none focus:ring-2 focus:ring-success-100"
                    >
                      🌍 기후 시나리오 이미지 더보기
                    </button>
                      <p className="text-sm text-black mt-2">
                      SSP 2.6과 SSP 8.5 시나리오의 상세한 기후 변화 예측 이미지를 확인하세요
                    </p>
                  </div>
                </div>
                )}

                {/* 회사 검색이 완료된 경우 회사별 기후시나리오 이미지 표시 */}
                {companyOverview && (
                  <div>
                    <div className="bg-green-50 border border-green-200 rounded-brand p-4 mb-6">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-semibold text-green-800">
                          📍 {companyOverview.종목명 || companyName} 기후시나리오 분석
                        </h3>
                        <div className="flex space-x-2">
                          <button
                            onClick={openHelpModal}
                            className="px-3 py-1.5 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors flex items-center space-x-1"
                          >
                            <span>📖</span>
                            <span>기후 시나리오란?</span>
                          </button>
                          <button
                            onClick={openScenarioModal}
                            className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-1"
                          >
                            <span>❓</span>
                            <span>사용법</span>
                          </button>
                          <button
                            onClick={() => window.open('/기후시나리오(SSP).pdf', '_blank')}
                            className="px-3 py-1.5 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 transition-colors flex items-center space-x-1"
                          >
                            <span>📄</span>
                            <span>PDF로 보기</span>
                          </button>
                        </div>
                      </div>
                      <p className="text-green-700 text-sm">
                        해당 기업의 생산시설이 위치한 지역의 기후변화 시나리오를 확인할 수 있습니다.
                      </p>
                    </div>

                    {/* 연도별 탭 선택 */}
                    <div className="mb-6">
                      <div className="flex space-x-1 bg-gray-200 p-1 rounded-lg">
                        <button
                          onClick={() => setSelectedYear('2026-2030')}
                          className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                            selectedYear === '2026-2030'
                              ? 'bg-white text-blue-600 shadow-sm'
                              : 'text-gray-600 hover:text-gray-800'
                          }`}
                        >
                          2026-2030년
                        </button>
                        <button
                          onClick={() => setSelectedYear('2025-2035-2050')}
                          className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                            selectedYear === '2025-2035-2050'
                              ? 'bg-white text-blue-600 shadow-sm'
                              : 'text-gray-600 hover:text-gray-800'
                          }`}
                        >
                          넷제로2050
                        </button>
                      </div>
                    </div>

                    {/* 지역별 탭 선택 */}
                    <div className="mb-6">
                      <div className="flex flex-wrap gap-2">
                        <button
                          onClick={() => setSelectedRegion('')}
                          className={`px-4 py-2 rounded-md font-medium transition-colors ${
                            selectedRegion === ''
                              ? 'bg-blue-600 text-white shadow-sm'
                              : 'bg-gray-200 text-gray-600 hover:text-gray-800'
                          }`}
                        >
                          전체 지역
                        </button>
                        {(() => {
                          // 회사별 지역 매핑
                          const companyRegions: Record<string, string[]> = {
                            '한온시스템': ['강남구', '경주시', '평택시', '아산시', '대덕구', '울주군'],
                            '현대모비스': ['포항시', '의왕시', '창원시', '진천군', '강남구', '성남시', '경주시', '아산시', '울주군', '달성군'],
                            'HL만도': ['화성시', '익산시', '원주시', '성남시', '평택시', '연수구']
                          };
                          
                          // 회사명 정규화 (대소문자, 공백 제거)
                          const normalizedCompanyName = companyName.replace(/\s+/g, '').toLowerCase();
                          let regions: string[] = [];
                          
                          for (const [company, companyRegionsList] of Object.entries(companyRegions)) {
                            if (normalizedCompanyName.includes(company.toLowerCase().replace(/\s+/g, ''))) {
                              regions = companyRegionsList;
                              break;
                            }
                          }
                          
                          return regions.map((region) => (
                            <button
                              key={region}
                              onClick={() => setSelectedRegion(region)}
                              className={`px-4 py-2 rounded-md font-medium transition-colors ${
                                selectedRegion === region
                                  ? 'bg-blue-600 text-white shadow-sm'
                                  : 'bg-gray-200 text-gray-600 hover:text-gray-800'
                              }`}
                            >
                              {region}
                            </button>
                          ));
                        })()}
                      </div>
                    </div>

                    {/* 2026-2030년 탭 내용 */}
                    {selectedYear === '2026-2030' && (
                      <div className="space-y-6">
                        <h4 className="text-xl font-semibold text-gray-800">2026-2030년 기후변화 예측</h4>
                        
                        {/* SSP 시나리오별 탭 */}
                        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-4">
                          <button
                            onClick={() => setSelectedSSP('SSP126')}
                            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
                              selectedSSP === 'SSP126'
                                ? 'bg-white text-blue-600 shadow-sm'
                                : 'text-gray-600 hover:text-gray-800'
                            }`}
                          >
                            SSP 1-2.6 (저탄소)
                          </button>
                          <button
                            onClick={() => setSelectedSSP('SSP585')}
                            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
                              selectedSSP === 'SSP585'
                                ? 'bg-white text-blue-600 shadow-sm'
                                : 'text-gray-600 hover:text-gray-800'
                            }`}
                          >
                            SSP 5-8.5 (고탄소)
                          </button>
                        </div>

                        {/* 기후지표별 이미지 그리드 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {getCompanyClimateImages(companyName, selectedSSP, '2026-2030', selectedRegion).map((image, index) => (
                            <div key={index} className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
                              <div className="p-4">
                                <h5 className="font-semibold text-gray-800 mb-2">{image.title}</h5>
                                <p className="text-sm text-gray-600 mb-3">{image.description}</p>
                                <div className="relative aspect-video bg-gray-100 rounded-md overflow-hidden">
                                  <img
                                    src={image.src}
                                    alt={image.title}
                                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-200 cursor-pointer"
                                    onClick={() => openImageModal(image.src, image.title)}
                                  />
                                  {/* 다운로드 버튼 */}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      downloadImage(image.src, image.title);
                                    }}
                                    className="absolute top-2 right-2 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors shadow-lg"
                                    title="이미지 다운로드"
                                  >
                                    <span className="text-sm">⬇️</span>
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 2025/2035/2050년 탭 내용 */}
                    {selectedYear === '2025-2035-2050' && (
                      <div className="space-y-6">
                        <h4 className="text-xl font-semibold text-gray-800">넷제로2050 기후변화 예측</h4>
                        
                        {/* SSP 시나리오별 탭 */}
                        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-4">
                          <button
                            onClick={() => setSelectedSSP('SSP126')}
                            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
                              selectedSSP === 'SSP126'
                                ? 'bg-white text-blue-600 shadow-sm'
                                : 'text-gray-600 hover:text-gray-800'
                            }`}
                          >
                            SSP 1-2.6 (저탄소)
                          </button>
                          <button
                            onClick={() => setSelectedSSP('SSP585')}
                            className={`flex-1 py-2 px-4 rounded-md font-medium transition-colors ${
                              selectedSSP === 'SSP585'
                                ? 'bg-white text-blue-600 shadow-sm'
                                : 'text-gray-600 hover:text-gray-800'
                            }`}
                          >
                            SSP 5-8.5 (고탄소)
                          </button>
                        </div>

                        {/* 기후지표별 이미지 그리드 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {getCompanyClimateImages(companyName, selectedSSP, '2025-2035-2050', selectedRegion).map((image, index) => (
                            <div key={index} className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
                              <div className="p-4">
                                <h5 className="font-semibold text-gray-800 mb-2">{image.title}</h5>
                                <p className="text-sm text-gray-600 mb-3">{image.description}</p>
                                <div className="relative aspect-video bg-gray-100 rounded-md overflow-hidden">
                                  <img
                                    src={image.src}
                                    alt={image.title}
                                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-200 cursor-pointer"
                                    onClick={() => openImageModal(image.src, image.title)}
                                  />
                                  {/* 다운로드 버튼 */}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      downloadImage(image.src, image.title);
                                    }}
                                    className="absolute top-2 right-2 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors shadow-lg"
                                    title="이미지 다운로드"
                                  >
                                    <span className="text-sm">⬇️</span>
                                  </button>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 일반 SSP 시나리오 섹션 추가 */}
                    <div className="mt-12 pt-8 border-t-2 border-gray-200">
                      <div className="bg-blue-50 border border-blue-200 rounded-brand p-4 mb-6">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-lg font-semibold text-blue-800">
                            🌍 한반도 기후시나리오 시나리오
                          </h3>
                          <div className="flex space-x-2">
                            <button
                              onClick={openHelpModal}
                              className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-1"
                            >
                              <span>📖</span>
                              <span>기후 시나리오란?</span>
                            </button>
                            <button
                              onClick={openScenarioModal}
                              className="px-3 py-1.5 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 transition-colors flex items-center space-x-1"
                            >
                              <span>❓</span>
                              <span>도움말</span>
                            </button>
                          </div>
                        </div>
                        <p className="text-blue-700 text-sm">
                          SSP126과 SSP585 시나리오의 전반적인 기후변화 예측을 확인할 수 있습니다.
                        </p>
                      </div>

                      {/* SSP 시나리오별 탭 */}
                      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg mb-6">
                        <button
                          onClick={() => setSelectedSSP('SSP126')}
                          className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                            selectedSSP === 'SSP126'
                              ? 'bg-white text-blue-600 shadow-sm'
                              : 'text-gray-600 hover:text-gray-800'
                          }`}
                        >
                          SSP 1-2.6 (저탄소)
                        </button>
                        <button
                          onClick={() => setSelectedSSP('SSP585')}
                          className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                            selectedSSP === 'SSP585'
                              ? 'bg-white text-blue-600 shadow-sm'
                              : 'text-gray-600 hover:text-gray-800'
                          }`}
                        >
                          SSP 5-8.5 (고탄소)
                        </button>
                      </div>

                      {/* 기후지표 카테고리별 탭 */}
                      <div className="flex flex-wrap gap-2 mb-6">
                        <button
                          onClick={() => setSelectedCategory('all')}
                          className={`px-4 py-2 rounded-md font-medium transition-colors ${
                            selectedCategory === 'all'
                              ? 'bg-blue-600 text-white shadow-sm'
                              : 'bg-gray-200 text-gray-600 hover:text-gray-800'
                          }`}
                        >
                          전체
                        </button>
                        <button
                          onClick={() => setSelectedCategory('temperature')}
                          className={`px-4 py-2 rounded-md font-medium transition-colors ${
                            selectedCategory === 'temperature'
                              ? 'bg-blue-600 text-white shadow-sm'
                              : 'bg-gray-200 text-gray-600 hover:text-gray-800'
                          }`}
                        >
                          온도 관련
                        </button>
                        <button
                          onClick={() => setSelectedCategory('precipitation')}
                          className={`px-4 py-2 rounded-md font-medium transition-colors ${
                            selectedCategory === 'precipitation'
                              ? 'bg-blue-600 text-white shadow-sm'
                              : 'bg-gray-200 text-gray-600 hover:text-gray-800'
                          }`}
                        >
                          강수 관련
                        </button>
                        <button
                          onClick={() => setSelectedCategory('extreme')}
                          className={`px-4 py-2 rounded-md font-medium transition-colors ${
                            selectedCategory === 'extreme'
                              ? 'bg-blue-600 text-white shadow-sm'
                              : 'bg-gray-200 text-gray-600 hover:text-gray-800'
                          }`}
                        >
                          극한 현상
                        </button>
                      </div>

                      {/* SSP 126 (저탄소) 시나리오 설명 */}
                      {selectedSSP === 'SSP126' && (
                        <div className="bg-info-50 p-6 rounded-brand border border-info-200">
                          <h4 className="text-xl font-semibold text-info-800 mb-3">SSP 1-2.6 (극저탄소 시나리오)</h4>
                          <p className="text-info-700 mb-4 text-lg">2100년까지 1.6°C 온도 상승, 파리협정 목표 달성</p>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                            {getFilteredGeneralClimateImages('SSP126', selectedCategory).map((image, index) => (
                              <div key={index} className="bg-white rounded-lg border border-info-200 shadow-sm overflow-hidden">
                                <div className="p-4">
                                  <h5 className="font-semibold text-gray-800 mb-2">{image.title}</h5>
                                  <p className="text-sm text-gray-600 mb-3">{image.description}</p>
                                  <div className="relative aspect-video bg-gray-100 rounded-md overflow-hidden">
                                    <img
                                      src={image.src}
                                      alt={image.title}
                                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-200 cursor-pointer"
                                      onClick={() => openImageModal(image.src, image.title)}
                                    />
                                    {/* 다운로드 버튼 */}
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        downloadImage(image.src, image.title);
                                      }}
                                      className="absolute top-2 right-2 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors shadow-lg"
                                      title="이미지 다운로드"
                                    >
                                      <span className="text-sm">⬇️</span>
                                    </button>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* SSP 585 (고탄소) 시나리오 설명 */}
                      {selectedSSP === 'SSP585' && (
                        <div className="bg-danger-50 p-6 rounded-brand border border-danger-200">
                          <h4 className="text-xl font-semibold text-danger-800 mb-3">SSP 5-8.5 (고탄소 시나리오)</h4>
                          <p className="text-danger-700 mb-4 text-lg">2100년까지 4.9°C 온도 상승, 극단적인 기후 변화</p>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
                            {getFilteredGeneralClimateImages('SSP585', selectedCategory).map((image, index) => (
                              <div key={index} className="bg-white rounded-lg border border-danger-200 shadow-sm overflow-hidden">
                                <div className="p-4">
                                  <h5 className="font-semibold text-gray-800 mb-2">{image.title}</h5>
                                  <p className="text-sm text-gray-600 mb-3">{image.description}</p>
                                  <div className="relative aspect-video bg-gray-100 rounded-md overflow-hidden">
                                    <img
                                      src={image.src}
                                      alt={image.title}
                                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-200 cursor-pointer"
                                      onClick={() => openImageModal(image.src, image.title)}
                                    />
                                    {/* 다운로드 버튼 */}
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        downloadImage(image.src, image.title);
                                      }}
                                      className="absolute top-2 right-2 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors shadow-lg"
                                      title="이미지 다운로드"
                                    >
                                      <span className="text-sm">⬇️</span>
                                    </button>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 탭 5: AI보고서 초안 */}
            {activeTab === 5 && (
              <div>
                <h2 className="text-2xl font-bold text-primary-600 mb-6">🤖 AI보고서 초안</h2>
                
                {/* AI 보고서 생성 버튼 */}
                <div className="bg-gradient-to-r from-blue-50 via-purple-50 to-green-50 p-8 rounded-brand border-2 border-primary-300 mb-8 shadow-lg">
                  <div className="text-center mb-6">
                    <h3 className="text-2xl font-bold text-gray-800 mb-2">🤖 AI 기반 TCFD 보고서 생성</h3>
                    <p className="text-gray-600">두 개의 AI 모델이 동시에 분석하여 비교 가능한 보고서를 생성합니다</p>
                    </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                    <div className="bg-white p-4 rounded-lg border border-blue-200 shadow-sm">
                      <div className="flex items-center mb-3">
                        <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center mr-3">
                          <span className="text-white font-bold text-sm">O</span>
                        </div>
                        <h4 className="font-semibold text-blue-700">OpenAI GPT-4o-mini</h4>
                      </div>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• 글로벌 최고 수준 언어 모델</li>
                        <li>• 정확한 사실 기반 응답</li>
                        <li>• 전문적인 비즈니스 용어</li>
                      </ul>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg border border-purple-200 shadow-sm">
                      <div className="flex items-center mb-3">
                        <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center mr-3">
                          <span className="text-white font-bold text-sm">K</span>
                        </div>
                        <h4 className="font-semibold text-purple-700">KoAlpaca/RoLA</h4>
                      </div>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• 한국어 특화 자연스러운 표현</li>
                        <li>• 모델 소유권으로 서버내에서 유출 가능성 낮음</li>
                        <li>• 저비용</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div className="text-center space-y-4">
                    {/* AI 모델 선택 */}
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold text-gray-800 mb-4 text-center">🤖 AI 모델 선택</h4>
                      <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        {/* OpenAI 모델 선택 */}
                        <button
                          onClick={() => setSelectedLLMModel('openai')}
                          className={`px-6 py-3 rounded-lg border-2 transition-all duration-300 focus:outline-none focus:ring-4 ${
                            selectedLLMModel === 'openai'
                              ? 'border-blue-500 bg-blue-50 text-blue-700 ring-blue-200'
                              : 'border-gray-300 bg-white text-gray-700 hover:border-blue-300 hover:bg-blue-50'
                          }`}
                        >
                          <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
                            <span className="font-medium">OpenAI GPT-4o-mini</span>
                          </div>
                        </button>
                        
                        {/* KoAlpaca 모델 선택 */}
                        <button
                          onClick={() => setSelectedLLMModel('huggingface')}
                          className={`px-6 py-3 rounded-lg border-2 transition-all duration-300 focus:outline-none focus:ring-4 ${
                            selectedLLMModel === 'huggingface'
                              ? 'border-purple-500 bg-purple-50 text-purple-700 ring-purple-200'
                              : 'border-gray-300 bg-white text-gray-700 hover:border-purple-300 hover:bg-purple-50'
                          }`}
                        >
                          <div className="flex items-center space-x-2">
                            <div className="w-4 h-4 bg-purple-500 rounded-full"></div>
                            <span className="font-medium">KoAlpaca/RoLA</span>
                          </div>
                        </button>
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3 justify-center">
                      <button 
                        onClick={handleGenerateTCFDReport}
                        disabled={isGenerating || !selectedLLMModel}
                        className={`px-8 py-4 rounded-brand shadow-lg transition-all duration-300 focus:outline-none focus:ring-4 font-semibold text-lg ${
                          !selectedLLMModel
                            ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                            : selectedLLMModel === 'openai'
                            ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 focus:ring-blue-200'
                            : 'bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700 focus:ring-purple-200'
                        }`}
                      >
                        {isGenerating ? (
                    <div className="flex items-center">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                            {selectedLLMModel === 'openai' ? 'OpenAI' : 'KoAlpaca'} 모델로 보고서를 생성하고 있습니다...
                    </div>
                        ) : (
                          `🚀 ${selectedLLMModel === 'openai' ? 'OpenAI' : selectedLLMModel === 'huggingface' ? 'KoAlpaca' : 'AI'} 보고서 생성 시작`
                        )}
                      </button>
                      
                      <button 
                        onClick={loadTcfdDatabaseData}
                        disabled={isLoadingDatabaseData}
                        className="px-6 py-4 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-brand shadow-lg hover:from-green-700 hover:to-teal-700 transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-green-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg"
                      >
                        {isLoadingDatabaseData ? (
                    <div className="flex items-center">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                            최신 데이터 로딩 중...
                    </div>
                        ) : (
                          '🔄 TCFD 데이터 새로고침'
                        )}
                      </button>
                    </div>
                    
                    <div className="space-y-2">
                      <p className="text-sm text-gray-500">
                        {!selectedLLMModel 
                          ? '🤖 AI 모델을 선택한 후 TCFD 프레임워크 탭에서 데이터를 입력하면 보고서를 생성할 수 있습니다'
                          : 'TCFD 프레임워크 탭에서 데이터를 입력한 후 생성할 수 있습니다'
                        }
                      </p>
                      {tcfdDatabaseData && (
                        <div className="space-y-1">
                                                  <p className="text-sm text-green-600 font-medium">
                          ✅ 데이터베이스에서 TCFD 입력 데이터를 성공적으로 가져와서 최신 데이터를 선택했습니다
                        </p>
                        <p className="text-xs text-gray-500">
                          📅 선택된 데이터 기준: {new Date(tcfdDatabaseData.created_at).toLocaleString('ko-KR')}
                        </p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* TCFD 데이터베이스 입력 데이터 표시 */}
                {tcfdDatabaseData ? (
                  <div className="mb-8">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-xl font-bold text-gray-800">📊 TCFD 프레임워크 입력 데이터</h3>
                      <div className="text-sm text-gray-600 bg-blue-50 px-3 py-1 rounded-full border border-blue-200">
                        📅 최신 데이터: {new Date(tcfdDatabaseData.created_at).toLocaleString('ko-KR')}
                      </div>
                    </div>
                    <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* 거버넌스 */}
                        <div>
                          <h4 className="font-semibold text-blue-700 mb-3 flex items-center">
                            <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                            거버넌스 (Governance)
                          </h4>
                          <div className="space-y-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">G1: 기후 관련 위험과 기회에 대한 감독</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.governance_g1 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">G2: 경영진의 기후 관련 위험과 기회 관리</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.governance_g2 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* 전략 */}
                        <div>
                          <h4 className="font-semibold text-green-700 mb-3 flex items-center">
                            <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                            전략 (Strategy)
                          </h4>
                          <div className="space-y-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">S1: 기후 관련 위험과 기회의 영향</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.strategy_s1 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">S2: 기후 관련 위험과 기회에 대한 대응</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.strategy_s2 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">S3: 재무계획에의 통합</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.strategy_s3 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* 리스크 관리 */}
                        <div>
                          <h4 className="font-semibold text-orange-700 mb-3 flex items-center">
                            <span className="w-3 h-3 bg-orange-500 rounded-full mr-2"></span>
                            리스크 관리 (Risk Management)
                          </h4>
                          <div className="space-y-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">R1: 기후 관련 위험 식별 및 평가</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.risk_management_r1 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">R2: 기후 관련 리스크 관리</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.risk_management_r2 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">R3: 리스크 관리 프로세스에의 통합</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.risk_management_r3 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* 지표 및 목표 */}
                        <div>
                          <h4 className="font-semibold text-purple-700 mb-3 flex items-center">
                            <span className="w-3 h-3 bg-purple-500 rounded-full mr-2"></span>
                            지표 및 목표 (Metrics & Targets)
                          </h4>
                          <div className="space-y-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">M1: 기후 관련 위험과 기회 평가 지표</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.metrics_targets_m1 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">M2: 기후 관련 기회 평가 지표</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.metrics_targets_m2 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-1">M3: 기후 관련 목표 설정</label>
                              <div className="bg-gray-50 p-3 rounded-md text-sm text-gray-800 min-h-[60px]">
                                {tcfdDatabaseData.metrics_targets_m3 || '입력된 데이터가 없습니다'}
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="mb-8">
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <div className="flex items-center">
                        <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center mr-3">
                          <span className="text-white text-sm">⚠️</span>
                    </div>
                        <div>
                          <h3 className="text-lg font-semibold text-yellow-800 mb-2">TCFD 데이터가 로드되지 않았습니다</h3>
                          <p className="text-yellow-700 mb-4">
                            TCFD 프레임워크에서 입력한 데이터를 데이터베이스에서 가져와야 합니다.
                          </p>
                          <button
                            onClick={loadTcfdDatabaseData}
                            disabled={isLoadingDatabaseData}
                            className="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {isLoadingDatabaseData ? '로딩 중...' : '🔄 TCFD 데이터 로드'}
                          </button>
                  </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* RAG 결과 표시 */}
                {ragResults.openai || ragResults.huggingface ? (
                  <div className="space-y-8">
                    <h3 className="text-xl font-bold text-gray-800 mb-6">AI 생성 TCFD 보고서</h3>
                    
                    {/* 결과 비교 헤더 */}
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border border-gray-200">
                      <h4 className="text-lg font-semibold text-gray-800 mb-2">🤖 AI 모델별 결과 비교</h4>
                      <p className="text-sm text-gray-600">
                        OpenAI GPT-4o-mini와 한국어 특화 KoAlpaca/RoLA 모델의 결과를 비교해보세요
                      </p>
                    </div>
                    
                    {/* OpenAI RAG 결과 */}
                    {ragResults.openai && (
                      <div className="border-2 border-blue-200 rounded-lg p-6 bg-gradient-to-br from-blue-50 to-blue-100 shadow-lg">
                        <div className="flex items-center mb-4">
                          <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center mr-3">
                            <span className="text-white font-bold text-lg">O</span>
                          </div>
                          <h4 className="text-xl font-bold text-blue-700">
                            🤖 OpenAI GPT-4o-mini
                          </h4>
                          <span className="ml-auto px-3 py-1 bg-blue-200 text-blue-800 rounded-full text-sm font-medium">
                            GPT-4o-mini
                          </span>
                        </div>
                        
                        <div className="space-y-6">
                          <div>
                            <h5 className="font-semibold text-gray-800 mb-3 flex items-center">
                              <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                              📝 초안 생성
                            </h5>
                            <div className="bg-white p-5 rounded-lg border border-blue-200 shadow-sm">
                              <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                                {ragResults.openai.draft}
                              </div>
                            </div>
                          </div>
                          
                          <div>
                            <h5 className="font-semibold text-gray-800 mb-3 flex items-center">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                              ✨ 윤문된 텍스트
                            </h5>
                            <div className="bg-green-50 p-5 rounded-lg border border-green-200 shadow-sm">
                              <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                                {ragResults.openai.polished}
                              </div>
                            </div>
                          </div>
                          
                          {/* 다운로드 버튼들 */}
                          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-blue-200">
                            <button
                              onClick={() => handleDownloadAsWord('openai')}
                              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                            >
                              <span>📄</span>
                              <span>Word 다운로드</span>
                            </button>
                            <button
                              onClick={() => handleDownloadAsPDF('openai')}
                              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center space-x-2"
                            >
                              <span>📕</span>
                              <span>PDF 다운로드</span>
                  </button>
                          </div>
                </div>
              </div>
            )}

                    {/* Hugging Face RAG 결과 */}
                    {ragResults.huggingface && (
                      <div className="border-2 border-purple-200 rounded-lg p-6 bg-gradient-to-br from-purple-50 to-purple-100 shadow-lg">
                        <div className="flex items-center mb-4">
                          <div className="w-10 h-10 bg-purple-500 rounded-full flex items-center justify-center mr-3">
                            <span className="text-white font-bold text-lg">K</span>
                          </div>
                          <h4 className="text-xl font-bold text-purple-700">
                            🚀 한국어 특화 KoAlpaca/RoLA
                          </h4>
                          <span className="ml-auto px-3 py-1 bg-purple-200 text-purple-800 rounded-full text-sm font-medium">
                            KoAlpaca 3.8B
                          </span>
                        </div>
                        
                        <div className="space-y-6">
                          <div>
                            <h5 className="font-semibold text-gray-800 mb-3 flex items-center">
                              <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                              📝 초안 생성
                            </h5>
                            <div className="bg-white p-5 rounded-lg border border-purple-200 shadow-sm">
                              <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                                {ragResults.huggingface.draft}
                              </div>
                            </div>
                          </div>
                          
                          <div>
                            <h5 className="font-semibold text-gray-800 mb-3 flex items-center">
                              <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                              ✨ 윤문된 텍스트
                            </h5>
                            <div className="bg-green-50 p-5 rounded-lg border border-green-200 shadow-sm">
                              <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
                                {ragResults.huggingface.polished}
                              </div>
                            </div>
                          </div>
                          
                          {/* 다운로드 버튼들 */}
                          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-purple-200">
                            <button
                              onClick={() => handleDownloadAsWord('huggingface')}
                              className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center space-x-2"
                            >
                              <span>📄</span>
                              <span>Word 다운로드</span>
                            </button>
                            <button
                              onClick={() => handleDownloadAsPDF('huggingface')}
                              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center space-x-2"
                            >
                              <span>📕</span>
                              <span>PDF 다운로드</span>
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    결과 요약 및 비교

                  </div>
                ) : (
                  <div className="text-center py-16">
                    {generatedReport ? (
                      // 생성된 보고서가 있을 때
                      <div className="bg-white p-8 rounded-lg border border-gray-200 max-w-4xl mx-auto text-left">
                        <div className="flex items-center justify-between mb-6">
                          <h3 className="text-2xl font-bold text-gray-800">생성된 TCFD 보고서</h3>
                          <div className="flex items-center space-x-3">
                            <span className="text-sm text-green-600 bg-green-50 px-3 py-1 rounded-full">
                              ✅ {reportGenerationStatus}
                            </span>
                            <button
                              onClick={() => setGeneratedReport('')}
                              className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                            >
                              새로 생성
                            </button>
                          </div>
                        </div>
                        
                        {/* 보고서 내용 */}
                        <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 max-h-96 overflow-y-auto">
                          <div 
                            className="prose prose-sm max-w-none text-black [&>*]:text-black [&_h1]:text-black [&_h2]:text-black [&_h3]:text-black [&_p]:text-black [&_li]:text-black [&_strong]:text-black [&_em]:text-black"
                            dangerouslySetInnerHTML={{ 
                              __html: generatedReport.replace(/\n/g, '<br/>').replace(/##/g, '<h2>').replace(/#/g, '<h1>') 
                            }}
                          />
                        </div>
                        
                        {/* 다운로드 버튼들 */}
                        <div className="flex justify-center space-x-4 mt-6">
                          <button
                            onClick={() => downloadReportAsText(generatedReport, 'tcfd-report.txt')}
                            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                          >
                            <span>📄</span>
                            <span>텍스트 다운로드</span>
                          </button>
                          <button
                            onClick={() => downloadReportAsWord(generatedReport, 'tcfd-report.docx')}
                            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2"
                          >
                            <span>📝</span>
                            <span>Word 다운로드</span>
                          </button>
                        </div>
                      </div>
                    ) : (
                      // 기존의 AI 보고서 생성 준비 완료 메시지
                      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-8 rounded-lg border border-gray-200 max-w-2xl mx-auto">
                        <div className="w-20 h-20 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center mx-auto mb-6">
                          <span className="text-white text-3xl">🤖</span>
                        </div>
                        <h3 className="text-xl font-semibold text-gray-800 mb-4">AI 보고서 생성 준비 완료</h3>
                        <p className="text-gray-600 mb-6">
                          두 개의 AI 모델이 TCFD 프레임워크 기반으로 보고서를 생성할 준비가 되었습니다.
                        </p>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                          <div className="bg-white p-3 rounded-lg border border-blue-200">
                            <div className="flex items-center">
                              <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center mr-2">
                                <span className="text-white text-xs font-bold">O</span>
                              </div>
                              <span className="text-sm font-medium text-blue-700">OpenAI GPT-4o-mini</span>
                            </div>
                          </div>
                          <div className="bg-white p-3 rounded-lg border border-purple-200">
                            <div className="flex items-center">
                              <div className="w-6 h-6 bg-purple-500 rounded-full flex items-center justify-center mr-2">
                                <span className="text-xs font-bold">K</span>
                              </div>
                              <span className="text-sm font-medium text-purple-700">KoAlpaca/RoLA</span>
                            </div>
                          </div>
                        </div>
                        
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                          <p className="text-sm text-yellow-800">
                            💡 <strong>다음 단계:</strong> TCFD 프레임워크 탭에서 11개 핵심 인덱스 데이터를 입력한 후, 
                            위의 &ldquo;AI 보고서 생성 시작&rdquo; 버튼을 클릭하세요.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* 기후시나리오 상세보기 모달 */}
        {isClimateModalOpen && selectedScenario && (
          <ClimateScenarioModal
            isOpen={isClimateModalOpen}
            scenario={selectedScenario}
            onClose={closeClimateModal}
          />
        )}

        {/* 기후시나리오 이미지 모달 */}
        {isImageModalOpen && selectedImage && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-2xl max-w-4xl max-h-[90vh] overflow-hidden">
              {/* 헤더 */}
              <div className="flex items-center justify-between p-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-800">{selectedImage.title}</h3>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => downloadImage(selectedImage.src, selectedImage.title)}
                    className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-1"
                  >
                    <span>⬇️</span>
                    <span>다운로드</span>
                  </button>
                  <button
                    onClick={closeImageModal}
                    className="w-8 h-8 bg-gray-200 hover:bg-gray-300 rounded-full flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
                  >
                    <span className="text-gray-600 font-bold text-lg">×</span>
                  </button>
                </div>
              </div>
              
              {/* 이미지 */}
              <div className="p-4">
                <img
                  src={selectedImage.src}
                  alt={selectedImage.title}
                  className="w-full h-auto max-h-[70vh] object-contain rounded-lg"
                />
              </div>
            </div>
          </div>
        )}

        {/* 기후 데이터 생성 모달 */}
        {showClimateDataModal && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">직접 기후 데이터 생성</h2>
                  <button
                    onClick={closeClimateDataModal}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                {/* 도움말 */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <div className="flex items-start">
                    <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="text-sm text-blue-800">
                      <p className="font-medium mb-1">💡 기후 시나리오 막대그래프 차트 생성</p>
                                              <p>선택한 조건에 맞는 기후 데이터를 막대그래프 차트로 시각화하여 이미지로 생성합니다.</p>
                      <p className="mt-1 text-blue-600">• SSP1-2.6: 저탄소 시나리오 (온실가스 배출량 감소)</p>
                      <p className="text-blue-600">• SSP5-8.5: 고탄소 시나리오 (온실가스 배출량 증가)</p>
                    </div>
                  </div>
                </div>

                {/* 기후 데이터 설정 폼 */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  {/* 시나리오 선택 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      기후 시나리오
                    </label>
                    <select
                      value={climateDataSettings.scenario}
                      onChange={(e) => setClimateDataSettings({...climateDataSettings, scenario: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    >
                      <option value="SSP126">SSP1-2.6 (저탄소 시나리오)</option>
                      <option value="SSP585">SSP5-8.5 (고탄소 시나리오)</option>
                    </select>
                  </div>

                  {/* 기후 변수 선택 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      기후 변수
                    </label>
                    <select
                      value={climateDataSettings.variable}
                      onChange={(e) => setClimateDataSettings({...climateDataSettings, variable: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    >
                      <option value="HW33">폭염일수 (최고기온 33°C 이상)</option>
                      <option value="RN">연강수량 (mm)</option>
                      <option value="TA">연평균기온 (°C)</option>
                      <option value="TR25">열대야일수 (최저기온 25°C 이상)</option>
                      <option value="RAIN80">호우일수 (일강수량 80mm 이상)</option>
                    </select>
                  </div>

                  {/* 시작 연도 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      시작 연도
                    </label>
                    <select
                      value={climateDataSettings.startYear}
                      onChange={(e) => setClimateDataSettings({...climateDataSettings, startYear: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    >
                      {Array.from({length: 80}, (_, i) => 2021 + i).map(year => (
                        <option key={year} value={year}>{year}년</option>
                      ))}
                    </select>
                  </div>

                  {/* 종료 연도 */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      종료 연도
                    </label>
                    <select
                      value={climateDataSettings.endYear}
                      onChange={(e) => setClimateDataSettings({...climateDataSettings, endYear: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                    >
                      {Array.from({length: 80}, (_, i) => 2021 + i).map(year => (
                        <option key={year} value={year}>{year}년</option>
                      ))}
                    </select>
                  </div>

                  {/* 추가 연도 입력 */}
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="block text-sm font-medium text-gray-700">
                        추가 연도
                      </label>
                      <button
                        type="button"
                        onClick={addAdditionalYear}
                        className="px-2 py-1 text-sm bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors flex items-center space-x-1"
                      >
                        <span className="text-lg">+</span>
                        <span>추가</span>
                      </button>
                    </div>
                    
                    {/* 추가 연도 입력 필드들 */}
                    {climateDataSettings.additionalYears.map((year, index) => (
                      <div key={index} className="flex items-center space-x-2 mb-2">
                        <select
                          value={year}
                          onChange={(e) => updateAdditionalYear(index, parseInt(e.target.value))}
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                        >
                          {Array.from({length: 80}, (_, i) => 2021 + i).map(yearOption => (
                            <option key={yearOption} value={yearOption}>{yearOption}년</option>
                          ))}
                        </select>
                        <button
                          type="button"
                          onClick={() => removeAdditionalYear(index)}
                          className="px-2 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors"
                        >
                          -
                        </button>
                      </div>
                    ))}
                    
                    {climateDataSettings.additionalYears.length === 0 && (
                      <p className="text-sm text-gray-500 italic">추가 연도를 입력하려면 + 버튼을 클릭하세요</p>
                    )}
                  </div>

                  {/* 행정구역 선택 */}
                  <div className="relative">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      행정구역
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={regionSearchTerm}
                        onChange={(e) => handleRegionSearch(e.target.value)}
                        onFocus={handleRegionFocus}
                        placeholder="행정구역을 입력하세요 (예: 강남구, 화성시)"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-black"
                      />
                      {showRegionDropdown && filteredRegions.length > 0 && (
                        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                          {filteredRegions.map((region, index) => (
                            <div
                              key={region.region_code}
                              onClick={() => selectRegion(region)}
                              className="px-3 py-2 hover:bg-gray-100 cursor-pointer text-sm border-b border-gray-100 last:border-b-0"
                            >
                              <div className="font-medium text-gray-900">{region.sub_region_name}</div>
                              <div className="text-xs text-gray-500">{region.region_name}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    {/* 전체 지역 선택 버튼 */}
                    <button
                      type="button"
                      onClick={() => {
                        setClimateDataSettings({...climateDataSettings, region: '전체 지역'});
                        setRegionSearchTerm('');
                        setShowRegionDropdown(false);
                      }}
                      className="mt-2 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors"
                    >
                      전체 지역 선택
                    </button>
                  </div>
                </div>

                {/* 기후 데이터 생성 버튼 */}
                <div className="flex justify-center mb-6">
                  <button
                    onClick={generateClimateData}
                    disabled={isGeneratingClimateData}
                    className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                  >
                    {isGeneratingClimateData ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>생성 중...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        <span>기후 데이터 생성</span>
                      </>
                    )}
                  </button>
                </div>

                {/* 생성된 기후 데이터 표시 */}
                {generatedClimateData && (
                  <div className="border-2 border-dashed border-green-300 rounded-lg p-4 bg-green-50">
                    <div className="text-center mb-4">
                      <div className="flex items-center justify-center mb-2">
                        <svg className="w-6 h-6 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <h3 className="text-lg font-semibold text-green-900">
                          기후 데이터 테이블 이미지 생성 완료!
                        </h3>
                      </div>
                      <p className="text-sm text-green-700 mb-3">
                        {climateDataSettings.scenario === 'SSP126' ? 'SSP1-2.6 (저탄소)' : 'SSP5-8.5 (고탄소)'} - 
                        {climateDataSettings.variable === 'HW33' ? '폭염일수' : 
                         climateDataSettings.variable === 'RN' ? '연강수량' :
                         climateDataSettings.variable === 'TA' ? '연평균기온' :
                         climateDataSettings.variable === 'TR25' ? '열대야일수' : '호우일수'}
                        ({climateDataSettings.startYear}년 ~ {climateDataSettings.endYear}년)
                        {climateDataSettings.region !== '전체 지역' ? ` - ${climateDataSettings.region}` : ''}
                      </p>
                    </div>
                    
                    <div className="flex justify-center mb-4">
                      <img
                        src={generatedClimateData}
                        alt="생성된 기후 막대그래프 차트"
                        className="max-w-full h-auto rounded-lg shadow-lg border border-gray-200"
                        onLoad={() => console.log('✅ 이미지 렌더링 성공')}
                        onError={(e) => {
                          console.error('❌ 이미지 렌더링 실패:', e);
                          console.error('❌ 이미지 소스:', generatedClimateData.substring(0, 100));
                        }}
                      />
                    </div>
                    
                    <div className="flex justify-center space-x-4">
                      <button
                        onClick={downloadGeneratedClimateData}
                        className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2 shadow-md"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span>PNG 다운로드</span>
                      </button>
                      
                      <button
                        onClick={() => setGeneratedClimateData(null)}
                        className="px-6 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors flex items-center space-x-2"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        <span>새로 만들기</span>
                      </button>
                    </div>
                    
                    <div className="mt-4 text-center">
                      <p className="text-xs text-green-600">
                        💡 생성된 이미지는 보고서, 프레젠테이션, 문서 등에 활용할 수 있습니다.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* 기후시나리오 도움말 모달 */}
        {isHelpModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-brand shadow-soft p-8 max-w-4xl mx-4 relative max-h-[90vh] overflow-y-auto">
              {/* X 버튼 */}
              <button
                onClick={closeHelpModal}
                className="absolute top-4 right-4 w-8 h-8 bg-gray-200 hover:bg-gray-300 rounded-full flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                <span className="text-gray-600 font-bold text-lg">×</span>
              </button>
              
              {/* 제목 */}
              <h2 className="text-2xl font-bold text-blue-600 mb-6 text-center">🌍 기후시나리오 이용가이드</h2>
              
              {/* 가이드 내용 */}
              <div className="space-y-6">
                <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                  <h3 className="text-xl font-semibold text-blue-800 mb-3">📊 기후시나리오란?</h3>
                  <p className="text-gray-700 mb-3">
                    기후시나리오는 미래의 기후 변화를 예측하기 위해 다양한 사회경제적 발전 경로와 온실가스 배출 시나리오를 조합한 것입니다. 
                    이를 통해 기업과 투자자들이 기후 관련 위험과 기회를 파악하고, 장기적인 의사결정을 내릴 수 있도록 도움을 줍니다.
                    SSP(Shared Socioeconomic Pathways)는 기후변화에 대한 사회경제적 발전 경로를 가정한 시나리오 체계로, 인구·경제·에너지 구조 등을 바탕으로 미래 기후 영향을 예측합니다.<br/>

                  </p>
                  
                  <div className="space-y-4">
                    <p className="text-gray-700">
                      <strong>SSP(Shared Socioeconomic Pathways)</strong>는 기후변화에 대한 사회경제적 발전 경로를 가정한 시나리오 체계입니다. 
                      인구·경제·에너지 구조 등을 바탕으로 미래 기후 영향을 예측합니다.
                    </p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                        <h4 className="font-semibold text-green-800 mb-2 flex items-center">
                          🌱 SSP1-2.6 (낙관적 저탄소 전환 시나리오)
                        </h4>
                        <p className="text-green-700 text-sm leading-relaxed">
                          글로벌 차원에서 탄소중립이 조기에 달성되고, 친환경 기술과 ESG 규제가 강화됩니다. 
                          기업은 지속가능 기술 투자, 저탄소 공급망 구축, 탄소배출 관리 역량 확보가 경쟁우위의 핵심입니다.
                        </p>
                      </div>
                      
                      <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                        <h4 className="font-semibold text-red-800 mb-2 flex items-center">
                          🔥 SSP5-8.5 (비관적 고탄소 시나리오)
                        </h4>
                        <p className="text-red-700 text-sm leading-relaxed">
                          화석연료 중심 성장으로 인해 4℃ 이상 온도 상승이 예상되며, 극한기상·규제 리스크가 폭발적으로 증가합니다. 
                          이 경우 기업은 물리적 리스크 관리(홍수·폭염·공급망 차질)와 기후규제 충격에 대응하는 비용 부담이 가중됩니다.
                        </p>
                      </div>
                    </div>
                    
                    <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                      <p className="text-blue-800 text-sm leading-relaxed">
                        <strong>➡️ 핵심 포인트:</strong> 따라서 기업은 두 시나리오를 동시에 고려해 
                        <strong>Transition Risk(전환 리스크)</strong>와 <strong>Physical Risk(물리적 리스크)</strong>를 
                        균형 있게 평가하고, 중장기 전략 시뮬레이션을 통해 대응 방안을 마련해야 합니다.
                      </p>
                    </div>
                    
                    <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                      <p className="text-gray-600 text-xs">
                        <strong>참고:</strong> 숫자 2.6과 8.5는 각각 2100년의 방사강제력(W/m²) 수준을 의미하며, 기후변화의 심각도를 나타냅니다.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                    <h4 className="text-lg font-semibold text-green-800 mb-3">🌱 SSP 1-2.6 (저탄소 시나리오)</h4>
                    <ul className="text-gray-700 space-y-2 text-sm">
                      <li>• <strong>온도 상승:</strong> 2100년까지 1.6°C</li>
                      <li>• <strong>배출 경로:</strong> 급격한 탄소 감소</li>
                      <li>• <strong>목표:</strong> 파리협정 1.5°C 달성</li>
                      <li>• <strong>특징:</strong> 지속가능한 발전 모델</li>
                    </ul>
                  </div>

                  <div className="bg-red-50 p-6 rounded-lg border border-red-200">
                    <h4 className="text-lg font-semibold text-red-800 mb-3">🔥 SSP 5-8.5 (고탄소 시나리오)</h4>
                    <ul className="text-gray-700 space-y-2 text-sm">
                      <li>• <strong>온도 상승:</strong> 2100년까지 4.4°C</li>
                      <li>• <strong>배출 경로:</strong> 현재 수준 유지</li>
                      <li>• <strong>위험:</strong> 극한 기후 현상 증가</li>
                      <li>• <strong>특징:</strong> 화석연료 의존 지속</li>
                    </ul>
                  </div>
                </div>

                <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200">
                  <h4 className="text-lg font-semibold text-yellow-800 mb-3">📈 기후지표 카테고리</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-semibold text-yellow-700 mb-2">🌡️ 온도 관련</h5>
                      <p className="text-gray-700 text-sm">평균기온, 최고기온, 최저기온 변화</p>
                    </div>
                    <div>
                      <h5 className="font-semibold text-yellow-700 mb-2">💧 강수 관련</h5>
                      <p className="text-gray-700 text-sm">강수량, 강수일수, 최대강수량 변화</p>
                    </div>
                    <div>
                      <h5 className="font-semibold text-yellow-700 mb-2">⚡ 극한 현상</h5>
                      <p className="text-gray-700 text-sm">폭염일수, 한파일수, 태풍 영향</p>
                    </div>
                    <div>
                      <h5 className="font-semibold text-yellow-700 mb-2">🌍 전체</h5>
                      <p className="text-gray-700 text-sm">모든 기후지표 통합 보기</p>
                    </div>
                  </div>
                </div>

                <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                  <h4 className="text-lg font-semibold text-purple-800 mb-3">🎯 활용 방법</h4>
                  <ol className="text-gray-700 space-y-2 text-sm">
                    <li><strong>1.</strong> SSP 시나리오 선택 (SSP126 또는 SSP585)</li>
                    <li><strong>2.</strong> 관심 있는 기후지표 카테고리 선택</li>
                    <li><strong>3.</strong> 이미지 클릭하여 상세 보기</li>
                    <li><strong>4.</strong> 회사별 지역 데이터와 비교 분석</li>
                    <li><strong>5.</strong> TCFD 보고서 작성 시 참고 자료로 활용</li>
                  </ol>
                </div>
              </div>
              
              {/* 닫기 버튼 */}
              <div className="mt-8 text-center">
                <button
                  onClick={closeHelpModal}
                  className="px-6 py-2 bg-blue-600 text-white rounded-brand shadow-soft hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-100"
                >
                  확인
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 시나리오란? 모달 */}
        {isScenarioModalOpen && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-brand shadow-soft p-8 max-w-4xl mx-4 relative max-h-[90vh] overflow-y-auto">
              {/* X 버튼 */}
              <button
                onClick={closeScenarioModal}
                className="absolute top-4 right-4 w-8 h-8 bg-gray-200 hover:bg-gray-300 rounded-full flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                <span className="text-gray-600 font-bold text-lg">×</span>
              </button>
              
              {/* 제목 */}
              <h2 className="text-2xl font-bold text-blue-600 mb-6 text-center">📖 기후시나리오 사용법</h2>
              
              {/* 내용 */}
              <div className="space-y-6">
                {/* 기본 흐름 */}
                <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                  <h3 className="text-xl font-semibold text-blue-800 mb-3">📋 기본 흐름</h3>
                  <div className="space-y-3 text-gray-700">
                    <div className="flex items-start space-x-2">
                      <span className="text-blue-600 font-bold">1.</span>
                      <span><strong>기간 선택:</strong> 상단에서 분석 구간을 고릅니다. (예: 2026–2030)</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <span className="text-blue-600 font-bold">2.</span>
                      <span><strong>지역 선택:</strong> 강남구/경주시/평택시/아산시/대덕구/울주군 중 하나를 클릭합니다.</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <span className="text-blue-600 font-bold">3.</span>
                      <span><strong>시나리오 선택:</strong> SSP 1-2.6(저탄소) 또는 SSP 5-8.5(고탄소) 탭을 누릅니다.</span>
                    </div>
                    <div className="flex items-start space-x-2">
                      <span className="text-blue-600 font-bold">4.</span>
                      <span><strong>그래프 읽기:</strong> 선택한 지역 기준으로 카드(그래프)가 갱신됩니다.</span>
                    </div>
                  </div>
                </div>

                {/* 그래프 읽기 가이드 */}
                <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                  <h4 className="text-lg font-semibold text-green-800 mb-3">📊 그래프 읽기</h4>
                  <div className="space-y-3 text-gray-700">
                    <div>
                      <p className="mb-2"><strong>단위:</strong></p>
                      <ul className="list-disc list-inside space-y-1 text-sm">
                        <li>연간 강수량: 단위 mm</li>
                        <li>호우일수/폭염일수/열대야일수: 단위 일</li>
                      </ul>
                    </div>
                    <div>
                      <p className="mb-2"><strong>값 읽기:</strong></p>
                      <p className="text-sm">막대 높이=예측 값입니다. (막대 위 숫자가 보이면 그 값을 읽어주세요.)</p>
                    </div>
                  </div>
                </div>

                {/* 대응 방안 */}
                <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200">
                  <h4 className="text-lg font-semibold text-yellow-800 mb-3">⚡ 대응 방안 (EX)</h4>
                  <div className="space-y-4">
                    <div className="bg-white p-4 rounded-lg">
                      <h5 className="font-semibold text-yellow-700 mb-2">🌧️ 호우일수 ↑</h5>
                      <ul className="text-gray-700 text-sm space-y-1">
                        <li>• 출하·납품 버퍼 1–2일 설정, 대체운송 루트 준비</li>
                        <li>• 전기실/컴프레서룸 방수턱·집수정 점검, 창고 랙 최저단 상향</li>
                        <li>• 체크: OTD(납기), 물류 리드타임, 침수 임계 초과시간</li>
                      </ul>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg">
                      <h5 className="font-semibold text-yellow-700 mb-2">💧 연간 강수량 ↑ / ↓</h5>
                      <ul className="text-gray-700 text-sm space-y-1">
                        <li>• ↑: 도장부스 RH/이슬점 관리 강화, 방습 포장 적용</li>
                        <li>• ↓: RO/DI 수처리 여유 용량·재이용수 비중 점검</li>
                        <li>• 체크: 도장 불량률, 수처리 설비 부하율</li>
                      </ul>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg">
                      <h5 className="font-semibold text-yellow-700 mb-2">🔥 폭염일수 ↑</h5>
                      <ul className="text-gray-700 text-sm space-y-1">
                        <li>• 전력 피크 요금 대비: ESS/DR 검토, 일부 공정 야간 전환</li>
                        <li>• 칠러/냉각탑 용량 재점검(오일·금형 온도 상한 지정)</li>
                        <li>• 체크: 피크 kW, kWh/Unit, 라인정지·트립 건수</li>
                      </ul>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg">
                      <h5 className="font-semibold text-yellow-700 mb-2">🌙 열대야일수 ↑</h5>
                      <ul className="text-gray-700 text-sm space-y-1">
                        <li>• 야간 프리쿨링 운영, 첫 차수 전수검사</li>
                        <li>• 금형/유압유 온도 SOP(야간 기준치) 적용</li>
                        <li>• 체크: 첫 차수 불량률, 스크랩률, 사이클타임 변동</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* 실제 피해 사례 */}
                <div className="bg-red-50 p-6 rounded-lg border border-red-200">
                  <h4 className="text-lg font-semibold text-red-800 mb-3">⚠️ 실제 피해 경고</h4>
                  <div className="space-y-4">
                    <div className="bg-white p-4 rounded-lg">
                      <h5 className="font-semibold text-red-700 mb-2">🇩🇪 독일(2021)</h5>
                      <p className="text-gray-700 text-sm mb-2">아르 계곡 홍수로 ZF 아르바일러 공장 침수 → ZF는 <strong>침수 안전 지역으로 생산 이전(2026 예정)</strong>을 결정했습니다.</p>
                      <p className="text-red-600 text-sm font-semibold">&ldquo;한 번의 홍수가 공장 이전으로 이어질 수 있습니다.&rdquo;</p>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg">
                      <h5 className="font-semibold text-red-700 mb-2">🇸🇮 슬로베니아(2023)</h5>
                      <p className="text-gray-700 text-sm mb-2">부품사 KLS Ljubno 침수 → VW 포르투갈 공장 일시 중단.</p>
                      <p className="text-red-600 text-sm font-semibold">&ldquo;한 협력사의 침수가 해외 라인 셧다운으로 번집니다.&rdquo;</p>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg">
                      <h5 className="font-semibold text-red-700 mb-2">🇮🇳 인도 첸나이(2015)</h5>
                      <p className="text-gray-700 text-sm mb-2">집중호우로 Apollo Tyres 오라가담 공장 가동 중단, 생산손실 약 450톤.</p>
                      <p className="text-red-600 text-sm font-semibold">&ldquo;창고/설비 침수는 즉시 생산 손실로 이어집니다.&rdquo;</p>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg">
                      <h5 className="font-semibold text-red-700 mb-2">🇮🇳 인도 케랄라(2018)</h5>
                      <p className="text-gray-700 text-sm mb-2">홍수로 Apollo Tyres 2개 공장 가동 중단, 손실 1,500–3,000톤 보고.</p>
                      <p className="text-red-600 text-sm font-semibold">&ldquo;피해는 설비뿐 아니라 인력 접근 불가로도 발생합니다.&rdquo;</p>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg">
                      <h5 className="font-semibold text-red-700 mb-2">🇹🇭 태국(2011)</h5>
                      <p className="text-gray-700 text-sm mb-2">아유타야·파툼타니 산업단지 대규모 침수 → 수백 개 부품/조립 공장 장기 중단, 글로벌 공급망 병목.</p>
                      <p className="text-red-600 text-sm font-semibold">&ldquo;지역 재난이 세계 생산차질로 확산됩니다.&rdquo;</p>
                    </div>
                    
                    <div className="bg-white p-4 rounded-lg">
                      <h5 className="font-semibold text-red-700 mb-2">🇨🇳 중국 쓰촨(2022)</h5>
                      <p className="text-gray-700 text-sm mb-2">기록적 폭염·가뭄으로 전력 제한, 도요타·CATL 등 공장 셧다운.</p>
                      <p className="text-red-600 text-sm font-semibold">&ldquo;폭염은 전력제한→생산중단의 트리거가 됩니다.&rdquo;</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* 닫기 버튼 */}
              <div className="mt-8 text-center">
                <button
                  onClick={closeScenarioModal}
                  className="px-6 py-2 bg-green-600 text-white rounded-brand shadow-soft hover:bg-green-700 transition-colors focus:outline-none focus:ring-2 focus:ring-green-100"
                >
                  확인
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TCFD 상세보기 모달 */}
        {isTcfdDetailModalOpen && selectedTcfdCategory && (
          <TCFDDetailModal
            isOpen={isTcfdDetailModalOpen}
            onClose={closeTcfdDetailModal}
            category={selectedTcfdCategory.category}
            title={selectedTcfdCategory.title}
            description={selectedTcfdCategory.description}
            disclosures={selectedTcfdCategory.disclosures}
            color={selectedTcfdCategory.color}
            bgColor={selectedTcfdCategory.bgColor}
          />
        )}

           {/* 이용가이드 박스 */}
           {isGuideOpen && (
             <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
               <div className="bg-white rounded-brand shadow-soft p-8 max-w-2xl mx-4 relative">
                 {/* X 버튼 */}
                 <button
                   onClick={() => setIsGuideOpen(false)}
                   className="absolute top-4 right-4 w-8 h-8 bg-gray-200 hover:bg-gray-300 rounded-full flex items-center justify-center transition-colors focus:outline-none focus:ring-2 focus:ring-gray-500"
                 >
                   <span className="text-gray-600 font-bold text-lg">×</span>
                 </button>
                 
                 {/* 제목 */}
                 <h2 className="text-2xl font-bold text-primary-600 mb-6 text-center">TCFD 이용가이드</h2>
                 
                 {/* 가이드 내용 */}
                 <div className="space-y-4">
                   <div className="flex items-start space-x-3">
                     <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 mt-1">
                       1
                     </div>
                     <div>
                       <h3 className="font-semibold text-gray-800 mb-1">회사정보 탭</h3>
                       <p className="text-gray-600 text-sm">회사명을 검색하여 해당 회사의 기본 정보를 확인하세요</p>
                     </div>
                   </div>
                   
                   <div className="flex items-start space-x-3">
                     <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 mt-1">
                       2
                     </div>
                     <div>
                       <h3 className="font-semibold text-gray-800 mb-1">재무정보 탭</h3>
                       <p className="text-gray-600 text-sm">재무 데이터와 손익계산서, 임원, 직원의 정보를 확인하세요</p>
                     </div>
                   </div>
                   
                   <div className="flex items-start space-x-3">
                     <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 mt-1">
                       3
                     </div>
                     <div>
                       <h3 className="font-semibold text-gray-800 mb-1">TCFD 프레임워크 탭</h3>
                       <p className="text-gray-600 text-sm">11개 핵심 인덱스를 입력하여 TCFD 보고서를 작성하세요</p>
                     </div>
                   </div>
                   
                   <div className="flex items-start space-x-3">
                     <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 mt-1">
                       4
                     </div>
                     <div>
                       <h3 className="font-semibold text-gray-800 mb-1">기후시나리오 탭</h3>
                       <p className="text-gray-600 text-sm">SSP 1-2.6과 SSP 5-8.5 시나리오의 기후 변화 예측을 확인하세요<br/>※ 해당 기업의 사업장 및 한반도의 기후시나리오에 따른 기후변화 예측 가능<br/>※ 자사의 확장, 공급망 리시크 대응에 활용할 수 있는 맞춤형 그래프 생성</p>
                     </div>
                   </div>
                   
                   <div className="flex items-start space-x-3">
                     <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 mt-1">
                       5
                     </div>
                     <div>
                       <h3 className="font-semibold text-gray-800 mb-1">AI보고서 초안 탭</h3>
                       <p className="text-gray-600 text-sm">입력된 정보를 바탕으로 AI가 자동으로 보고서를 생성합니다<br/>필요한 윤문들은 txt,Word로 받으세요</p>
                     </div>
                   </div>
                 </div>
                 
                 {/* 닫기 버튼 */}
                 <div className="mt-8 text-center">
                   <button
                     onClick={() => setIsGuideOpen(false)}
                     className="px-6 py-2 bg-primary-600 text-white rounded-brand shadow-soft hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-100"
                   >
                     확인
                   </button>
                 </div>
               </div>
             </div>
           )}
        </div>
      </div>
    </div>
  );
}
