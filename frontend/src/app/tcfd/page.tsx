'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ClimateScenarioModal, TCFDDetailModal } from '@/ui/molecules';
import { Header } from '@/ui/organisms';
import { apiClient, tcfdReportAPI, tcfdAPI, authService } from '@/shared/lib';
import { useAuthStore } from '@/shared/state/auth.store';
import axios from 'axios';

// 컬럼명 한국어 매핑 객체
const COLUMN_LABELS: { [key: string]: string } = {
  // 1️⃣ 전체기업 정보
  'Id': '아이디',
  'Stock_code': '종목코드',
  'Companyname': '회사명',
  'Market': '시장',
  'Dart_code': 'DART 고유 코드',
  
  // 2️⃣ 재무 정보
  'Debt': '부채',
  'Debt_ratio': '부채비율',
  'Liability': '총부채',
  'Netdebt': '순부채',
  'Netdebt_ratio': '순부채비율',
  'Capital_stock': '자본금',
  'Equity': '자본총계',
  'Asset': '자산총계',
  'Long-Term Debt': '장기부채',
  'Total Debt': '총부채',
  'Cash': '현금',
  'Year': '연도',
  
  // 3️⃣ 임원 정보
  'Corp_code': '법인코드',
  'Nm': '성명',
  'Sexdstn': '성별',
  'Birth Ym': '생년월',
  'Ofcps': '직위(직책)',
  'Rgist Exctv At': '등기임원 여부',
  'Fte At': '상근 여부',
  'Chrg Job': '담당업무',
  'Main Career': '주요 경력',
  'Mxxm Shrholdr Relate': '최대주주와의 관계',
  'Hffc Pd': '재임 기간',
  'Tenure End On': '임기 종료일',
  
  // 4️⃣ 노동·급여 정보
  'Fo Bbm': '외국인 이사 수',
  'Rgllbr Co': '정규직 근로자 수',
  'Rgllbr_abacpt_labrr_co': '정규직 외 수탁/용역 근로자 수',
  'Cnttk Co': '계약직 근로자 수',
  'Cnttk_abacpt_labrr_co': '계약직 외 수탁/용역 근로자 수',
  'Sm': '소속 노동조합 조합원 수',
  'Avrg Cnwk Sdytrn': '평균 근속연수',
  'Fyer Salary Totamt': '연간 급여 총액',
  'Jan Salary Am': '1인당 평균 급여액'
};

// 컬럼명을 한국어로 변환하는 함수
const getKoreanLabel = (englishLabel: string): string => {
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

// 5개 테이블 데이터 타입 (TCFD Service 응답 구조와 일치)
interface CompanyFinancialData {
  success: boolean;
  company_name: string;
  company_id?: string;
  found_in_table?: string;
  total_records?: number;
  tables?: string[];
  data: {
    employee: TableRecord[];
    profit: TableRecord[];
    executive: TableRecord[];
    financial: TableRecord[];
    corporation: TableRecord[];
  };
  message: string;
}

export default function TcfdSrPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState(1);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // 회사 검색 관련 상태
  const [companyName, setCompanyName] = useState(''); // 빈 문자열로 초기화
  const [companyFinancialData, setCompanyFinancialData] = useState<CompanyFinancialData | null>(null);
  const [isLoadingCompany, setIsLoadingCompany] = useState(false);
  const [companyError, setCompanyError] = useState<string | null>(null);
  
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
    metrics_targets_m3: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 회사 목록 로드 (사용하지 않음)
  const loadCompanies = async () => {
    // 회사 목록은 더 이상 로드하지 않음
  };

  // 회사별 재무정보 로드 (apiClient 사용)
  const loadCompanyFinancialData = async (companyName: string) => {
    if (!companyName.trim()) return;
    
    setIsLoadingCompany(true);
    setCompanyError(null);
    
    // 디버깅 로그 추가
    console.log('🔍 회사명:', companyName);
    console.log('🔍 인코딩된 회사명:', encodeURIComponent(companyName));
    
    try {
      const url = `/api/v1/tcfd/company-financial-data?company_name=${encodeURIComponent(companyName)}`;
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
      console.error('❌ 오류 발생:', error);
      if (axios.isAxiosError(error)) {
        setCompanyError(`재무정보 로드 실패: ${error.response?.status} - ${error.message}`);
      } else {
        setCompanyError(error instanceof Error ? error.message : '알 수 없는 오류');
      }
    } finally {
      setIsLoadingCompany(false);
    }
  };

  // 회사명 입력 시 재무정보 조회
  const handleCompanySearch = () => {
    if (companyName.trim()) {
      loadCompanyFinancialData(companyName);
    }
  };

  // 재무 분석 실행 함수는 더 이상 사용하지 않음

  // 상세보기 모달 열기
  const handleClimateDetails = (scenario: 'ssp2.6' | 'ssp8.5') => {
    setSelectedScenario(scenario);
    setIsClimateModalOpen(true);
  };

  // 상세보기 모달 닫기
  const closeClimateModal = () => {
    setIsClimateModalOpen(false);
    setSelectedScenario(null);
  };
  
  // TCFD 입력 데이터 변경 핸들러
  const handleTcfdInputChange = (field: string, value: string) => {
    setTcfdInputData(prev => ({
      ...prev,
      [field]: value
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
        ...tcfdInputData
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
        metrics_targets_m3: ''
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

  // TCFD 상세보기 모달 열기
  const handleTcfdDetails = (category: string, data: {
    title: string;
    description: string;
    disclosures: TCFDStandardData[];
    color: string;
    bgColor: string;
  }) => {
    setSelectedTcfdCategory({
      category,
      title: data.title,
      description: data.description,
      disclosures: data.disclosures,
      color: data.color,
      bgColor: data.bgColor
    });
    setIsTcfdDetailModalOpen(true);
  };

  // TCFD 상세보기 모달 닫기
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
        '지배구조': {
          title: '거버넌스',
          description: '기후 관련 위험과 기회에 대한 감독 및 책임',
          color: 'text-blue-700',
          bgColor: 'bg-blue-50',
          disclosures: []
        },
        '전략': {
          title: '전략',
          description: '기후 관련 위험과 기회가 비즈니스 모델에 미치는 영향',
          color: 'text-green-700',
          bgColor: 'bg-green-50',
          disclosures: []
        },
        '위험관리': {
          title: '위험관리',
          description: '기후 관련 위험 식별, 평가 및 관리',
          color: 'text-yellow-700',
          bgColor: 'bg-yellow-50',
          disclosures: []
        },
        '지표와 감축목표': {
          title: '지표 및 목표',
          description: '기후 관련 위험과 기회를 평가하고 관리하기 위한 지표 및 목표',
          color: 'text-purple-700',
          bgColor: 'bg-purple-50',
          disclosures: []
        }
      };

      // 데이터를 각 카테고리에 분류
      data.forEach(item => {
        if (frameworkData[item.category]) {
          frameworkData[item.category].disclosures.push(item);
        }
      });

      setTcfdStandards(frameworkData);
    } catch (err) {
      console.error("Failed to fetch TCFD standards:", err);
      if (axios.isAxiosError(err)) {
        setTcfdError(`TCFD 표준 정보 로드 실패: ${err.response?.status} - ${err.message}`);
      } else {
        setTcfdError("TCFD 표준 정보를 불러오는 데 실패했습니다.");
      }
    } finally {
      setIsLoadingTcfd(false);
    }
  };

  // 컴포넌트 마운트 시 회사 목록 로드
  useEffect(() => {
    loadCompanies();
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

          // 토큰이 있으면 실제 API로 인증 상태 확인
          console.log('🔍 토큰 존재, API로 인증 상태 확인 중...');
          
          try {
            // 인증 상태 확인 API 호출
            console.log('🔍 /api/v1/auth/verify API 호출 시작...');
            const response = await apiClient.get('/api/v1/auth/verify');
            console.log('✅ 인증 상태 확인 성공:', response.data);
            setIsAuthenticated(true);
            
            // 인증 성공 후에만 TCFD 표준 데이터 로드
            console.log('🔍 TCFD 표준 데이터 로드 시작...');
            await fetchTcfdStandards();
            
          } catch (authError: any) {
            console.log('⚠️ 인증 상태 확인 실패, 토큰 갱신 시도:', authError);
            
            // 401 에러가 아닌 경우에만 토큰 갱신 시도
            if (authError.response?.status === 401) {
              try {
                const refreshResponse = await apiClient.post('/api/v1/auth/refresh');
                console.log('✅ 토큰 갱신 성공:', refreshResponse.data);
                
                // 새 토큰을 localStorage에 저장
                if (refreshResponse.data.access_token) {
                  localStorage.setItem('auth_token', refreshResponse.data.access_token);
                  setIsAuthenticated(true);
                  
                  // 토큰 갱신 성공 후 TCFD 표준 데이터 로드
                  console.log('🔍 토큰 갱신 후 TCFD 표준 데이터 로드 시작...');
                  await fetchTcfdStandards();
                } else {
                  throw new Error('토큰 갱신 실패');
                }
                
              } catch (refreshError: any) {
                console.error('❌ 토큰 갱신 실패:', refreshError);
                // 토큰 갱신 실패 시에만 로그아웃 처리
                if (refreshError.response?.status === 401) {
                  alert('인증이 만료되었습니다. 다시 로그인해주세요.');
                  localStorage.removeItem('auth_token');
                  router.push('/login');
                } else {
                  // 네트워크 오류 등으로 인한 갱신 실패는 인증 상태 유지
                  console.log('⚠️ 네트워크 오류로 인한 토큰 갱신 실패, 인증 상태 유지');
                  setIsAuthenticated(true);
                  // 기존 토큰으로 TCFD 데이터 로드 시도
                  try {
                    await fetchTcfdStandards();
                  } catch (dataError) {
                    console.log('⚠️ TCFD 데이터 로드 실패, 나중에 재시도 가능');
                  }
                }
              }
            } else {
              // 401이 아닌 다른 오류는 네트워크 문제일 수 있으므로 인증 상태 유지
              console.log('⚠️ 네트워크 오류로 인한 인증 확인 실패, 인증 상태 유지');
              setIsAuthenticated(true);
              // 기존 토큰으로 TCFD 데이터 로드 시도
              try {
                await fetchTcfdStandards();
              } catch (dataError) {
                console.log('⚠️ TCFD 데이터 로드 실패, 나중에 재시도 가능');
              }
            }
          }
          
        } catch (error: any) {
          console.error('❌ 인증 확인 실패:', error);
          // 네트워크 오류 등으로 인한 실패는 인증 상태 유지
          if (error.response?.status === 401) {
            alert('인증 확인에 실패했습니다. 다시 로그인해주세요.');
            localStorage.removeItem('auth_token');
            router.push('/login');
          } else {
            console.log('⚠️ 네트워크 오류로 인한 인증 확인 실패, 인증 상태 유지');
            setIsAuthenticated(true);
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

  // 인증되지 않은 경우 로딩 화면 표시
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header />
        <div className="pt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">인증 확인 중...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 재무정보 표시 컴포넌트
  const renderFinancialTable = (data: TableRecord[] | undefined, title: string) => {
    console.log(`🔍 ${title} 렌더링:`, data);
    
    if (!data || data.length === 0) {
      console.log(`❌ ${title}: 데이터 없음`);
      return (
        <div className="text-center py-4 text-gray-500">
          {title} 데이터가 없습니다
        </div>
      );
    }
    
    console.log(`✅ ${title}: ${data.length}개 레코드`);

    const columns = Object.keys(data[0] || {});
    console.log(`🔍 ${title} 컬럼명:`, columns);

         // 재무상태, 전체기업 정보, 직원정보, 임원정보는 세로형태로 표시
     if (title === '재무상태' || title === '전체기업 정보' || title === '직원 정보' || title === '임원 정보') {
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
               
               if (title === '재무상태' && row.companyname) {
                 recordName = String(row.companyname);
               } else if (title === '전체기업 정보' && row.companyname) {
                 recordName = String(row.companyname);
               } else if (title === '직원 정보' && row.name) {
                 recordName = String(row.name);
               } else if (title === '임원 정보' && row.name) {
                 recordName = String(row.name);
               } else if (row.id) {
                 recordName = `ID: ${String(row.id)}`;
               }

               return (
                 <div key={index} className="bg-gray-100 border border-gray-300 rounded-brand p-4 shadow-soft">
                   <h4 className="font-medium text-gray-900 mb-3 text-sm">{recordName}</h4>
                   <div className="space-y-2">
                     {columns.map((column) => (
                       <div key={column} className="flex justify-between">
                         <span className="text-xs font-medium text-gray-600 capitalize">
                           {getKoreanLabel(column)}:
                         </span>
                         <span className="text-sm text-gray-900 text-right break-words max-w-[200px]">
                           {typeof row[column] === 'number' 
                             ? row[column].toLocaleString() 
                             : String(row[column] || '-')}
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
                 onClick={() => setShowAllStates(prev => ({ ...prev, [title]: !showAll }))}
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
                   <th key={column} className="px-4 py-2 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-b border-gray-300">
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
                       {typeof row[column] === 'number' 
                         ? row[column].toLocaleString() 
                         : String(row[column] || '-')}
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

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <div className="pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-section">
          {/* 헤더 */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-primary-600 mb-2">
              TCFD 기준으로 SR 작성
            </h1>
            <p className="text-gray-700">
              기후 관련 재무 공시를 위한 지속가능보고서 작성 도구
            </p>
          </div>

        {/* 탭 네비게이션 */}
        <div className="bg-white rounded-brand shadow-soft border border-gray-300 mb-6">
          <div className="border-b border-gray-300">
            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
              {[
                { id: 1, name: '회사정보', icon: '🏢' },
                { id: 2, name: '재무정보', icon: '💰' },
                { id: 3, name: 'TCFD 프레임워크', icon: '📊' },
                { id: 4, name: '기후시나리오', icon: '🌍' },
                { id: 5, name: 'AI보고서 초안', icon: '🤖' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap transition-colors
                    ${activeTab === tab.id
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-primary-600 hover:border-primary-300'
                    }
                  `}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* 탭 컨텐츠 */}
        <div className="bg-white rounded-brand shadow-soft border border-gray-300 p-6">
                     {/* 탭 1: 회사정보 */}
           {activeTab === 1 && (
             <div>
               <h2 className="text-2xl font-bold text-primary-600 mb-6">🏢 회사정보</h2>
               
               {/* 회사 검색 */}
               <div className="mb-6">
                 <div className="flex gap-4 items-end">
                   <div className="flex-1">
                     <label className="block text-sm font-medium text-gray-700 mb-2">
                       회사명 검색
                     </label>
                     <input
                       type="text"
                       value={companyName}
                       onChange={(e) => setCompanyName(e.target.value)}
                       placeholder="회사명을 입력하세요 (예: 한온시스템, 현대모비스, 만도)"
                       className="w-full px-4 py-2 border border-gray-300 rounded-brand focus:border-primary-600 focus:ring-2 focus:ring-primary-100 text-gray-900 placeholder-gray-500 bg-white transition-colors"
                       onKeyPress={(e) => e.key === 'Enter' && handleCompanySearch()}
                     />
                   </div>
                   <button
                     onClick={handleCompanySearch}
                     disabled={!companyName.trim() || isLoadingCompany}
                     className="px-6 py-2 bg-primary-600 text-white rounded-brand shadow-soft hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-primary-100"
                   >
                     {isLoadingCompany ? '검색 중...' : '검색'}
                   </button>
                 </div>
                
                {/* 사용 가능한 회사 목록은 제거됨 */}
              </div>

                             {/* 회사별 재무정보 표시 */}
               {companyFinancialData && (
                 <div className="mt-6">
                   <div className="bg-primary-100 border border-primary-300 rounded-brand p-4 mb-6">
                     <h3 className="text-lg font-semibold text-primary-700 mb-2">
                       📊 {companyFinancialData.company_name} 재무정보
                     </h3>
                                          <p className="text-primary-600">
                        {companyFinancialData.total_records ? `총 ${companyFinancialData.total_records}개 레코드` : ''}
                        {companyFinancialData.tables && companyFinancialData.tables.length > 0 
                          ? `, ${companyFinancialData.tables.join(', ')} 테이블`
                          : companyFinancialData.found_in_table ? `, ${companyFinancialData.found_in_table} 테이블에서 발견` : ''
                        }
                      </p>
                   </div>

                  {/* 5개 테이블 데이터 표시 */}
                  {renderFinancialTable(companyFinancialData.data?.employee, '직원 정보')}
                  {renderFinancialTable(companyFinancialData.data?.profit, '손익계산')}
                  {renderFinancialTable(companyFinancialData.data?.executive, '임원 정보')}
                  {renderFinancialTable(companyFinancialData.data?.financial, '재무상태')}
                  {renderFinancialTable(companyFinancialData.data?.corporation, '전체기업 정보')}
                </div>
              )}

                             {/* 에러 메시지 */}
               {companyError && (
                 <div className="mt-4 p-4 bg-danger-50 border border-danger-200 rounded-brand">
                   <p className="text-danger-700">{companyError}</p>
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
                  <div className="bg-success-50 border border-success-200 rounded-brand p-4 mb-6">
                    <h3 className="text-lg font-semibold text-success-700 mb-2">
                      📊 {companyFinancialData.company_name} 재무정보
                    </h3>
                                         <p className="text-success-600">
                       {companyFinancialData.total_records ? `총 ${companyFinancialData.total_records}개 레코드` : ''}
                       {companyFinancialData.tables && companyFinancialData.tables.length > 0 
                         ? `, ${companyFinancialData.tables.join(', ')} 테이블`
                         : companyFinancialData.found_in_table ? `, ${companyFinancialData.found_in_table} 테이블에서 발견` : ''
                       }
                     </p>
                  </div>

                  {/* 5개 테이블 데이터 표시 - 순서 변경 */}
                  {renderFinancialTable(companyFinancialData.data?.corporation, '전체기업 정보')}
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
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
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
                             <h5 className="font-medium text-gray-800 mb-2">공개 요구사항 ({data.disclosures.length}개):</h5>
                             {/* 첫 번째 항목만 미리보기로 표시 */}
                             <div className="bg-white p-3 rounded-brand shadow-soft border border-gray-300">
                               <h6 className="font-semibold text-gray-800 mb-1">{data.disclosures[0].disclosure_id}</h6>
                               <p className="text-sm text-gray-700 mb-1">{data.disclosures[0].disclosure_summary}</p>
                               <p className="text-xs text-gray-500">{data.disclosures[0].disclosure_detail}</p>
                             </div>
                             
                                                            {/* 더 많은 항목이 있을 경우 상세보기 버튼 표시 */}
                              {data.disclosures.length > 1 && (
                                <div className="text-center pt-2">
                                  <button
                                    onClick={() => handleTcfdDetails(category, data)}
                                    className={`px-4 py-2 ${data.color.replace('text-', 'bg-').replace('-700', '-600')} text-white rounded-brand shadow-soft hover:opacity-90 transition-colors text-sm font-medium border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-100`}
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

                             {/* TCFD 표준 상세 정보 */}
               <div>
                 <h3 className="text-xl font-semibold text-gray-800 mb-4">TCFD 표준 상세 정보</h3>
                 <div className="space-y-4">
                   {companyFinancialData ? (
                     <div className="bg-success-50 border border-success-200 rounded-brand p-4 mb-6">
                       <h4 className="text-lg font-semibold text-success-700 mb-2">
                         📊 {companyFinancialData.company_name} TCFD 분석
                       </h4>
                       <p className="text-success-600">
                         회사 정보와 재무 데이터를 기반으로 TCFD 프레임워크에 따른 분석을 진행할 수 있습니다.
                       </p>
                     </div>
                   ) : (
                     <div className="bg-primary-100 border border-primary-300 rounded-brand p-6 text-center mb-6">
                       <h4 className="text-lg font-semibold text-primary-700 mb-2">회사 검색이 필요합니다</h4>
                       <p className="text-primary-600 mb-4">
                         회사정보 탭에서 회사명을 검색하면 해당 회사의 TCFD 분석을 진행할 수 있습니다.
                       </p>
                       <button
                         onClick={() => setActiveTab(1)}
                         className="px-6 py-2 bg-primary-600 text-white rounded-brand shadow-soft hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-100"
                       >
                         회사정보 탭으로 이동
                       </button>
                     </div>
                   )}

                  {/* TCFD 11개 인덱스 입력 폼 */}
                  {companyFinancialData && (
                    <div className="mt-8">
                      <h4 className="text-lg font-semibold text-gray-800 mb-4">TCFD 11개 핵심 인덱스 데이터 입력</h4>
                      
                      {/* 거버넌스 */}
                      <div className="mb-6">
                        <h5 className="text-md font-semibold text-blue-700 mb-3 border-b border-blue-200 pb-2">거버넌스 (Governance)</h5>
                        <div className="space-y-4">
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              G1: 기후 관련 위험과 기회에 대한 이사회 감독
                            </label>
                                                                                     <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="이사회가 기후 관련 위험과 기회를 어떻게 감독하고 있는지 설명하세요..."
                              value={tcfdInputData.governance_g1}
                              onChange={(e) => handleTcfdInputChange('governance_g1', e.target.value)}
                            />
                             <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                               <p className="text-xs text-blue-700 font-medium mb-1">💡 예시:</p>
                                                               <p className="text-xs text-black">&ldquo;이사회는 기후변화 관련 주요 리스크와 기회를 정기적으로 검토하며, 연 2회 이상 ESG 위원회를 통해 관련 안건을 심의합니다.&rdquo;</p>
                             </div>
                          </div>
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              G2: 기후 관련 위험과 기회에 대한 경영진 역할
                            </label>
                                                                                     <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="경영진이 기후 관련 위험과 기회를 어떻게 관리하는지 설명하세요..."
                              value={tcfdInputData.governance_g2}
                              onChange={(e) => handleTcfdInputChange('governance_g2', e.target.value)}
                            />
                             <div className="mt-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                               <p className="text-xs text-blue-700 font-medium mb-1">💡 예시:</p>
                                                               <p className="text-xs text-black">&ldquo;경영진은 탄소중립 목표 달성을 위한 실행계획을 수립하고, 각 사업부에 KPI를 배분하여 이행 상황을 모니터링합니다.&rdquo;</p>
                             </div>
                          </div>
                        </div>
                      </div>

                      {/* 전략 */}
                      <div className="mb-6">
                        <h5 className="text-md font-semibold text-green-700 mb-3 border-b border-green-200 pb-2">전략 (Strategy)</h5>
                        <div className="space-y-4">
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              S1: 기후 관련 위험과 기회의 비즈니스 영향
                            </label>
                                                                                     <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="기후 관련 위험과 기회가 조직의 비즈니스, 전략, 재무 계획에 미치는 영향을 설명하세요..."
                              value={tcfdInputData.strategy_s1}
                              onChange={(e) => handleTcfdInputChange('strategy_s1', e.target.value)}
                            />
                             <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                               <p className="text-xs text-green-700 font-medium mb-1">💡 예시:</p>
                                                               <p className="text-xs text-black">&ldquo;기후변화로 인한 원자재 가격 변동은 당사 제조원가에 영향을 미칠 수 있으며, 이에 따라 공급망 다변화 전략을 추진하고 있습니다.&rdquo;</p>
                             </div>
                          </div>
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              S2: 전략적 영향의 실제 잠재적 영향
                            </label>
                            <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="조직의 전략, 비즈니스, 재무 계획에 미치는 기후 관련 위험과 기회의 실제 잠재적 영향을 설명하세요..."
                              value={tcfdInputData.strategy_s2}
                              onChange={(e) => handleTcfdInputChange('strategy_s2', e.target.value)}
                            />
                            <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                              <p className="text-xs text-green-700 font-medium mb-1">💡 예시:</p>
                              <p className="text-xs text-black">&ldquo;탄소중립 정책으로 인한 규제 강화는 당사 제품의 경쟁력을 재정의할 수 있으며, 친환경 기술 개발에 대한 투자를 확대하고 있습니다.&rdquo;</p>
                            </div>
                          </div>
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              S3: 기후 시나리오 분석
                            </label>
                            <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="조직이 사용하는 기후 시나리오 분석 방법과 결과를 설명하세요..."
                              value={tcfdInputData.strategy_s3}
                              onChange={(e) => handleTcfdInputChange('strategy_s3', e.target.value)}
                            />
                            <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                              <p className="text-xs text-green-700 font-medium mb-1">💡 예시:</p>
                              <p className="text-xs text-black">&ldquo;IPCC RCP 2.6 및 RCP 8.5 시나리오를 기반으로 2030년, 2050년, 2100년까지의 기후 변화 영향을 분석하여 장기 전략을 수립하고 있습니다.&rdquo;</p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* 리스크 관리 */}
                      <div className="mb-6">
                        <h5 className="text-md font-semibold text-yellow-700 mb-3 border-b border-yellow-200 pb-2">리스크 관리 (Risk Management)</h5>
                        <div className="space-y-4">
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              R1: 기후 관련 위험 식별 및 평가 프로세스
                            </label>
                            <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="조직이 기후 관련 위험을 식별, 평가, 관리하는 프로세스를 설명하세요..."
                              value={tcfdInputData.risk_management_r1}
                              onChange={(e) => handleTcfdInputChange('risk_management_r1', e.target.value)}
                            />
                            <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                              <p className="text-xs text-yellow-700 font-medium mb-1">💡 예시:</p>
                              <p className="text-xs text-black">&ldquo;기후 관련 위험은 분기별 리스크 평가 회의에서 식별하고, 위험도와 영향도를 매트릭스로 평가하여 우선순위를 정하고 있습니다.&rdquo;</p>
                            </div>
                          </div>
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              R2: 위험 관리 프로세스 통합
                            </label>
                            <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="조직의 전반적인 위험 관리 프로세스에 기후 관련 위험을 통합하는 방법을 설명하세요..."
                              value={tcfdInputData.risk_management_r2}
                              onChange={(e) => handleTcfdInputChange('risk_management_r2', e.target.value)}
                            />
                            <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                              <p className="text-xs text-yellow-700 font-medium mb-1">💡 예시:</p>
                              <p className="text-xs text-black">&ldquo;기후 관련 위험은 기존 ERM(Enterprise Risk Management) 프레임워크에 통합하여 전사적 위험 관리 체계의 일부로 운영하고 있습니다.&rdquo;</p>
                            </div>
                          </div>
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              R3: 기후 관련 위험을 전사적 위험 관리 프로세스에 통합
                            </label>
                            <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="기후 관련 위험을 조직의 전사적 위험 관리 프로세스에 어떻게 통합하고 있는지 설명하세요..."
                              value={tcfdInputData.risk_management_r3}
                              onChange={(e) => handleTcfdInputChange('risk_management_r3', e.target.value)}
                            />
                            <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                              <p className="text-xs text-yellow-700 font-medium mb-1">💡 예시:</p>
                              <p className="text-xs text-black">&ldquo;기후 관련 위험은 분기별 전사적 위험 평가에 포함되어 있으며, 위험도와 영향도를 정량적으로 평가하여 리스크 매트릭스에 반영하고 있습니다.&rdquo;</p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* 지표 및 목표 */}
                      <div className="mb-6">
                        <h5 className="text-md font-semibold text-purple-700 mb-3 border-b border-purple-200 pb-2">지표 및 목표 (Metrics and Targets)</h5>
                        <div className="space-y-4">
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              M1: 기후 관련 위험 평가 지표
                            </label>
                            <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="조직이 기후 관련 위험과 기회를 평가하는 데 사용하는 지표를 설명하세요..."
                              value={tcfdInputData.metrics_targets_m1}
                              onChange={(e) => handleTcfdInputChange('metrics_targets_m1', e.target.value)}
                            />
                            <div className="mt-2 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                              <p className="text-xs text-purple-700 font-medium mb-1">💡 예시:</p>
                              <p className="text-xs text-black">&ldquo;탄소 배출량(tCO2e), 에너지 효율성(단위당 에너지 소비량), 기후 관련 규제 준수율 등을 주요 지표로 사용하고 있습니다.&rdquo;</p>
                            </div>
                          </div>
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              M2: 기후 관련 기회 평가 지표
                            </label>
                            <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="기후 관련 위험과 기회를 평가하는 데 사용하는 지표를 설명하세요..."
                              value={tcfdInputData.metrics_targets_m2}
                              onChange={(e) => handleTcfdInputChange('metrics_targets_m2', e.target.value)}
                            />
                            <div className="mt-2 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                              <p className="text-xs text-purple-700 font-medium mb-1">💡 예시:</p>
                              <p className="text-xs text-black">&ldquo;친환경 제품 매출 비중, 재생에너지 사용률, 기후 관련 R&D 투자 비율 등을 기회 평가 지표로 활용하고 있습니다.&rdquo;</p>
                            </div>
                          </div>
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              M3: 기후 관련 목표 설정
                            </label>
                            <textarea
                              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                              rows={3}
                              placeholder="조직이 기후 관련 위험과 기회를 평가하는 데 사용하는 목표를 설명하세요..."
                              value={tcfdInputData.metrics_targets_m3}
                              onChange={(e) => handleTcfdInputChange('metrics_targets_m3', e.target.value)}
                            />
                            <div className="mt-2 p-3 bg-purple-50 border border-purple-200 rounded-lg">
                              <p className="text-xs text-purple-700 font-medium mb-1">💡 예시:</p>
                              <p className="text-xs text-black">&ldquo;2030년까지 탄소 배출량 30% 감축, 2050년까지 탄소중립 달성, 재생에너지 사용률 50% 달성 등의 목표를 설정하고 있습니다.&rdquo;</p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* 제출 버튼 */}
                      <div className="flex justify-center mt-8">
                        <button 
                          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                          onClick={handleTcfdSubmit}
                          disabled={isSubmitting}
                        >
                          {isSubmitting ? '저장 중...' : 'TCFD 분석 시작'}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

                     {/* 탭 4: 기후시나리오 */}
           {activeTab === 4 && (
             <div>
               <h2 className="text-2xl font-bold text-primary-600 mb-6">🌍 기후시나리오</h2>
               <div className="space-y-4">
                 <div className="bg-danger-50 p-4 rounded-brand border border-danger-200">
                   <h3 className="text-lg font-semibold text-danger-700 mb-2">RCP 8.5 (고탄소 시나리오)</h3>
                   <p className="text-danger-600 mb-4">2100년까지 4.9°C 온도 상승, 극단적인 기후 변화</p>
                   <button 
                     onClick={() => handleClimateDetails('ssp8.5')}
                     className="px-4 py-2 bg-danger-600 text-white rounded-brand shadow-soft hover:bg-danger-700 transition-colors text-sm focus:outline-none focus:ring-2 focus:ring-danger-100"
                   >
                     상세보기
                   </button>
                 </div>
                 <div className="bg-info-50 p-4 rounded-brand border border-info-200">
                   <h3 className="text-lg font-semibold text-info-700 mb-2">RCP 2.6 (극저탄소 시나리오)</h3>
                   <p className="text-info-600 mb-4">2100년까지 1.6°C 온도 상승, 파리협정 목표 달성</p>
                   <button 
                     onClick={() => handleClimateDetails('ssp2.6')}
                     className="px-4 py-2 bg-info-600 text-white rounded-brand shadow-soft hover:bg-info-700 transition-colors text-sm focus:outline-none focus:ring-2 focus:ring-info-100"
                   >
                     상세보기
                   </button>
                 </div>
                
                                                   {/* 기후 시나리오 이미지 갤러리로 이동하는 More 버튼 */}
                  <div className="mt-6 text-center">
                    <button
                      onClick={() => {
                        // 인증 상태 확인 후 이동
                        const token = localStorage.getItem('auth_token');
                        if (token) {
                          router.push('/climate-scenarios');
                        } else {
                          alert('로그인이 필요합니다. 먼저 로그인해주세요.');
                          router.push('/login');
                        }
                      }}
                      className="px-8 py-3 bg-success-600 text-white rounded-brand shadow-soft hover:bg-success-700 transition-colors font-medium text-lg focus:outline-none focus:ring-2 focus:ring-success-100"
                    >
                      🌍 기후 시나리오 이미지 더보기
                    </button>
                    <p className="text-sm text-gray-700 mt-2">
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
               <div className="bg-gradient-to-r from-primary-50 to-info-50 p-6 rounded-brand border border-primary-300">
                 <h3 className="text-lg font-semibold text-primary-700 mb-4">AI 기반 TCFD 보고서 생성</h3>
                 <div className="space-y-3">
                   <div className="flex items-center">
                     <span className="w-2 h-2 bg-primary-500 rounded-full mr-3"></span>
                     <span className="text-primary-700">회사 정보 및 재무 데이터 분석</span>
                   </div>
                   <div className="flex items-center">
                     <span className="w-2 h-2 bg-info-500 rounded-full mr-3"></span>
                     <span className="text-info-700">기후 위험 평가 및 시나리오 분석</span>
                   </div>
                   <div className="flex items-center">
                     <span className="w-2 h-2 bg-success-500 rounded-full mr-3"></span>
                     <span className="text-success-700">TCFD 프레임워크 기반 보고서 생성</span>
                   </div>
                   <div className="flex items-center">
                     <span className="w-2 h-2 bg-warning-500 rounded-full mr-3"></span>
                     <span className="text-warning-700">지속가능성 지표 및 권장사항 제시</span>
                   </div>
                 </div>
                 <button className="mt-6 px-6 py-3 bg-primary-600 text-white rounded-brand shadow-soft hover:bg-primary-700 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-100">
                   AI 보고서 생성 시작
                 </button>
               </div>
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
     </div>
     </div>
   );
 }
