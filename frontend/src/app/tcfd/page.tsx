'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ClimateScenarioModal, TCFDDetailModal } from '@/ui/molecules';
import { Header } from '@/ui/organisms';
import { apiClient, tcfdReportAPI, tcfdAPI, llmServiceAPI } from '@/shared/lib';

import axios from 'axios';

// 컬럼명 한국어 매핑 객체
const COLUMN_LABELS: { [key: string]: string } = {
  // 1️⃣ 전체기업 정보
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
  const [activeTab, setActiveTab] = useState(1);
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



  // 상세보기 모달 열기/닫기
  const handleClimateDetails = (scenario: 'ssp2.6' | 'ssp8.5') => {
    setSelectedScenario(scenario);
    setIsClimateModalOpen(true);
  };
  const closeClimateModal = () => {
    setIsClimateModalOpen(false);
    setSelectedScenario(null);
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

  // 2개 RAG 시스템으로 TCFD 보고서 생성 함수
  const handleGenerateTCFDReport = async () => {
    if (!companyFinancialData?.company_name) {
      alert('회사 정보가 필요합니다. 먼저 회사를 검색해주세요.');
      return;
    }

    // TCFD 입력 데이터가 충분한지 확인
    const hasInputData = Object.values(tcfdInputData).some(value => value.trim() !== '');
    if (!hasInputData) {
      alert('TCFD 입력 데이터가 필요합니다. TCFD 프레임워크 탭에서 데이터를 입력해주세요.');
      return;
    }

    setIsGenerating(true);
    
    try {
      // TCFD 입력 데이터를 새 API 형식에 맞춰 구성
      const tcfdReportRequest = {
        company_name: companyFinancialData.company_name,
        report_year: new Date().getFullYear().toString(),
        tcfd_inputs: {
          company_name: companyFinancialData.company_name,
          user_id: localStorage.getItem('user_id') || 'user123',
          governance_g1: tcfdInputData.governance_g1 || '',
          governance_g2: tcfdInputData.governance_g2 || '',
          strategy_s1: tcfdInputData.strategy_s1 || '',
          strategy_s2: tcfdInputData.strategy_s2 || '',
          strategy_s3: tcfdInputData.strategy_s3 || '',
          risk_management_r1: tcfdInputData.risk_management_r1 || '',
          risk_management_r2: tcfdInputData.risk_management_r2 || '',
          risk_management_r3: tcfdInputData.risk_management_r3 || '',
          metrics_targets_m1: tcfdInputData.metrics_targets_m1 || '',
          metrics_targets_m2: tcfdInputData.metrics_targets_m2 || '',
          metrics_targets_m3: tcfdInputData.metrics_targets_m3 || '',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        report_type: "draft",
        llm_provider: "openai"
      };

      console.log('🤖 TCFD 보고서 생성 시작:', tcfdReportRequest);

      // 2개 LLM 시스템으로 TCFD 보고서 생성
      const [openaiResult, hfResult] = await Promise.all([
        // OpenAI로 TCFD 보고서 생성
        generateTCFDReportWithLLM(tcfdReportRequest, "openai"),
        // Hugging Face로 TCFD 보고서 생성
        generateTCFDReportWithLLM(tcfdReportRequest, "huggingface")
      ]);

      console.log('✅ OpenAI TCFD 보고서 결과:', openaiResult);
      console.log('✅ Hugging Face TCFD 보고서 결과:', hfResult);

      // 결과를 기존 RAG 결과 형식에 맞춰 변환
      setRagResults({
        openai: {
          draft: openaiResult.report_content || '보고서 생성에 실패했습니다.',
          polished: openaiResult.report_content || '보고서 생성에 실패했습니다.'
        },
        huggingface: {
          draft: hfResult.report_content || '보고서 생성에 실패했습니다.',
          polished: hfResult.report_content || '보고서 생성에 실패했습니다.'
        }
      });

      // AI보고서 초안 탭으로 자동 이동
      setActiveTab(5);

    } catch (error) {
      console.error('❌ TCFD 보고서 생성 실패:', error);
      alert('TCFD 보고서 생성에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsGenerating(false);
    }
  };

  // LLM 서비스를 사용하여 TCFD 보고서 생성
  const generateTCFDReportWithLLM = async (request: any, llmProvider: string) => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        throw new Error('인증 토큰이 없습니다');
      }

      // llm-service의 TCFD API 호출
      const response = await fetch(`${process.env.NEXT_PUBLIC_LLM_SERVICE_URL || 'http://localhost:8002'}/tcfd/generate-report`, {
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

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
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
          title: '위험관리',
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

    // 재무상태, 전체기업 정보, 직원정보, 임원정보는 세로형태로 표시
    if (
      title === '재무상태' ||
      title === '전체기업 정보' ||
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
              } else if (title === '전체기업 정보' && (row as any).companyname) {
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
                        '전체기업 정보',
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
                            R2: 위험 관리 프로세스 통합
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="조직의 전반적인 위험 관리 프로세스에 기후 관련 위험을 통합하는 방법을 설명하세요..."
                            value={tcfdInputData.risk_management_r2}
                            onChange={(e) => handleTcfdInputChange('risk_management_r2', e.target.value)}
                          />
                          <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                            <p className="text-xs text-yellow-700 font-medium mb-1">💡 예시:</p>
                            <p className="text-xs text-black">
                              &ldquo;기후 관련 위험은 기존 ERM(Enterprise Risk Management) 프레임워크에 통합하여 전사적
                              위험 관리 체계의 일부로 운영하고 있습니다.&rdquo;
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
                            R3: 기후 관련 위험을 전사적 위험 관리 프로세스에 통합
                          </label>
                          <textarea
                            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black bg-white"
                            rows={3}
                            placeholder="기후 관련 위험을 조직의 전사적 위험 관리 프로세스에 어떻게 통합하고 있는지 설명하세요..."
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
                <div className="space-y-4">
                  <div className="bg-danger-50 p-4 rounded-brand border border-danger-200">
                    <h3 className="text-lg font-semibold text-black mb-2">SSP 8.5 (고탄소 시나리오)</h3>
                    <p className="text-black mb-4">2100년까지 4.9°C 온도 상승, 극단적인 기후 변화</p>
                    <button
                      onClick={() => handleClimateDetails('ssp8.5')}
                      className="px-4 py-2 bg-danger-600 text-black rounded-brand shadow-soft hover:bg-danger-700 transition-colors text-sm focus:outline-none focus:ring-2 focus:ring-danger-100"
                    >
                      상세보기
                    </button>
                  </div>

                  <div className="bg-info-50 p-4 rounded-brand border border-info-200">
                    <h3 className="text-lg font-semibold text-black mb-2">SSP 2.6 (극저탄소 시나리오)</h3>
                    <p className="text-black mb-4">2100년까지 1.6°C 온도 상승, 파리협정 목표 달성</p>
                    <button
                      onClick={() => handleClimateDetails('ssp2.6')}
                      className="px-4 py-2 bg-info-600 text-black rounded-brand shadow-soft hover:bg-info-700 transition-colors text-sm focus:outline-none focus:ring-2 focus:ring-info-100"
                    >
                      상세보기
                    </button>
                  </div>

                  {/* 기후 시나리오 이미지 갤러리로 이동하는 More 버튼 */}
                  <div className="mt-6 text-center">
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
                        <li>• 한국 기업 문화 이해</li>
                        <li>• ESG/TCFD 전문 용어</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <button 
                      onClick={handleGenerateTCFDReport}
                      disabled={isGenerating}
                      className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-brand shadow-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-blue-200 disabled:opacity-50 disabled:cursor-not-allowed font-semibold text-lg"
                    >
                      {isGenerating ? (
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                          AI 모델들이 보고서를 생성하고 있습니다...
                        </div>
                      ) : (
                        '🚀 AI 보고서 생성 시작'
                      )}
                    </button>
                    <p className="text-sm text-gray-500 mt-3">
                      TCFD 프레임워크 탭에서 데이터를 입력한 후 생성할 수 있습니다
                    </p>
                  </div>
                </div>

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
                        </div>
                      </div>
                    )}

                    {/* 결과 요약 및 비교 */}
                    <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
                      <h4 className="text-lg font-semibold text-gray-800 mb-4">📊 AI 모델별 특징 비교</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-white p-4 rounded-lg border border-blue-200">
                          <h5 className="font-semibold text-blue-700 mb-2">OpenAI GPT-4o-mini</h5>
                          <ul className="text-sm text-gray-600 space-y-1">
                            <li>• 글로벌 최고 수준의 언어 이해력</li>
                            <li>• 영어 기반 다국어 지원</li>
                            <li>• 정확한 사실 기반 응답</li>
                            <li>• 전문적인 비즈니스 용어</li>
                          </ul>
                        </div>
                        <div className="bg-white p-4 rounded-lg border border-purple-200">
                          <h5 className="font-semibold text-purple-700 mb-2">KoAlpaca/RoLA</h5>
                          <ul className="text-sm text-gray-600 space-y-1">
                            <li>• 한국어 특화 자연스러운 표현</li>
                            <li>• 한국 기업 문화 이해</li>
                            <li>• ESG/TCFD 전문 용어</li>
                            <li>• 로컬 컨텍스트 적합성</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-16">
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
                              <span className="text-white text-xs font-bold">K</span>
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
                       <p className="text-gray-600 text-sm">상세한 재무 데이터와 손익계산서 정보를 확인하세요</p>
                     </div>
                   </div>
                   
                   <div className="flex items-start space-x-3">
                     <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 mt-1">
                       3
                     </div>
                     <div>
                       <h3 className="font-semibold text-gray-800 mb-1">TCFD 프레임워크 탭</h3>
                       <p className="text-gray-600 text-sm">11개 핵심 인덱스를 입력하여 기후 관련 정보를 작성하세요</p>
                     </div>
                   </div>
                   
                   <div className="flex items-start space-x-3">
                     <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 mt-1">
                       4
                     </div>
                     <div>
                       <h3 className="font-semibold text-gray-800 mb-1">기후시나리오 탭</h3>
                       <p className="text-gray-600 text-sm">SSP 2.6과 SSP 8.5 시나리오의 기후 변화 예측을 확인하세요</p>
                     </div>
                   </div>
                   
                   <div className="flex items-start space-x-3">
                     <div className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center font-bold text-sm flex-shrink-0 mt-1">
                       5
                     </div>
                     <div>
                       <h3 className="font-semibold text-gray-800 mb-1">AI보고서 초안 탭</h3>
                       <p className="text-gray-600 text-sm">입력된 정보를 바탕으로 AI가 자동으로 보고서를 생성합니다</p>
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
