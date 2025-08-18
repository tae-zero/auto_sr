'use client';

import { useState, useEffect } from 'react';
import ClimateScenarioModal from '@/components/ClimateScenarioModal';
import axios from 'axios';

// TCFD 표준 데이터 타입 정의
interface TCFDStandardData {
  id: number;
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
  const [activeTab, setActiveTab] = useState(1);
  
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

  // TCFD 표준 데이터 상태 추가
  const [tcfdStandards, setTcfdStandards] = useState<TCFDFrameworkData>({});
  const [isLoadingTcfd, setIsLoadingTcfd] = useState(false);
  const [tcfdError, setTcfdError] = useState<string | null>(null);

  // 회사 목록 로드 (사용하지 않음)
  const loadCompanies = async () => {
    // 회사 목록은 더 이상 로드하지 않음
  };

  // 회사별 재무정보 로드 (axios 사용)
  const loadCompanyFinancialData = async (companyName: string) => {
    if (!companyName.trim()) return;
    
    setIsLoadingCompany(true);
    setCompanyError(null);
    
    // 디버깅 로그 추가
    console.log('🔍 회사명:', companyName);
    console.log('🔍 인코딩된 회사명:', encodeURIComponent(companyName));
    
    try {
      const url = `/api/company-financial-data?company_name=${encodeURIComponent(companyName)}`;
      console.log('🔍 요청 URL:', url);
      
      const response = await axios.get(url);
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

  // TCFD 표준 데이터 불러오기 (axios 사용)
  useEffect(() => {
    if (activeTab === 3) { // TCFD 프레임워크 탭일 때만 데이터 로드
      const fetchTcfdStandards = async () => {
        setIsLoadingTcfd(true);
        setTcfdError(null);
        try {
          // tcfdAPI 대신 직접 axios 사용
          const response = await axios.get('/api/v1/tcfd/standards');
          const data: TCFDStandardData[] = response.data;  // ✅ response.data.data 제거

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
      fetchTcfdStandards();
    }
  }, [activeTab]);

  // 컴포넌트 마운트 시 회사 목록 로드
  useEffect(() => {
    loadCompanies();
  }, []);

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

    // 재무상태, 전체기업 정보, 직원정보, 임원정보는 세로형태로 표시
    if (title === '재무상태' || title === '전체기업 정보' || title === '직원 정보' || title === '임원 정보') {
      const showAll = showAllStates[title] || false;
      const displayData = showAll ? data : data.slice(0, 6);
      const hasMore = data.length > 6;

      return (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3 text-blue-600">{title}</h3>
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
                <div key={index} className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-3 text-sm">{recordName}</h4>
                  <div className="space-y-2">
                    {columns.map((column) => (
                      <div key={column} className="flex justify-between">
                        <span className="text-xs font-medium text-gray-600 capitalize">
                          {column.replace(/_/g, ' ')}:
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
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
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
        <h3 className="text-lg font-semibold mb-3 text-blue-600">{title}</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border border-gray-200 rounded-lg">
            <thead className="bg-gray-50">
              <tr>
                {columns.map((column) => (
                  <th key={column} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.map((row, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  {columns.map((column) => (
                    <td key={column} className="px-4 py-3 text-sm text-gray-900 border-b">
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
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 헤더 */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            TCFD 기준으로 SR 작성
          </h1>
          <p className="text-gray-600">
            기후 관련 재무 공시를 위한 지속가능보고서 작성 도구
          </p>
        </div>

        {/* 탭 네비게이션 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="border-b border-gray-200">
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
                    py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                    ${activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
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
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          {/* 탭 1: 회사정보 */}
          {activeTab === 1 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🏢 회사정보</h2>
              
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
                      className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-black placeholder-gray-500 bg-white"
                      onKeyPress={(e) => e.key === 'Enter' && handleCompanySearch()}
                    />
                  </div>
                  <button
                    onClick={handleCompanySearch}
                    disabled={!companyName.trim() || isLoadingCompany}
                    className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoadingCompany ? '검색 중...' : '검색'}
                  </button>
                </div>
                
                {/* 사용 가능한 회사 목록은 제거됨 */}
              </div>

              {/* 회사별 재무정보 표시 */}
              {companyFinancialData && (
                <div className="mt-6">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <h3 className="text-lg font-semibold text-blue-900 mb-2">
                      📊 {companyFinancialData.company_name} 재무정보
                    </h3>
                                         <p className="text-blue-700">
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
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-red-700">{companyError}</p>
                </div>
              )}
            </div>
          )}

          {/* 탭 2: 재무정보 */}
          {activeTab === 2 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">💰 재무정보</h2>
              
              {/* 회사 검색 결과가 없을 때 안내 메시지 */}
              {!companyFinancialData && (
                <div className="text-center py-12">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-blue-900 mb-2">회사 검색이 필요합니다</h3>
                    <p className="text-blue-700 mb-4">
                      회사정보 탭에서 회사명을 검색하면 해당 회사의 재무정보가 여기에 표시됩니다.
                    </p>
                    <button
                      onClick={() => setActiveTab(1)}
                      className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      회사정보 탭으로 이동
                    </button>
                  </div>
                </div>
              )}

              {/* 회사별 재무정보 표시 */}
              {companyFinancialData && (
                <div>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                    <h3 className="text-lg font-semibold text-green-900 mb-2">
                      📊 {companyFinancialData.company_name} 재무정보
                    </h3>
                                         <p className="text-green-700">
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
              <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 TCFD 프레임워크</h2>
              
              {/* TCFD 표준 정보 표시 */}
              <div className="mb-8">
                <h3 className="text-xl font-semibold text-gray-800 mb-4">TCFD 표준 권고사항</h3>
                
                {isLoadingTcfd && (
                  <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                    <p className="mt-2 text-gray-600">TCFD 표준 정보를 불러오는 중...</p>
                  </div>
                )}

                {tcfdError && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                    <p className="text-red-700">{tcfdError}</p>
                  </div>
                )}

                {!isLoadingTcfd && !tcfdError && Object.keys(tcfdStandards).length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {Object.entries(tcfdStandards).map(([category, data]) => (
                      <div key={category} className={`${data.bgColor} p-6 rounded-lg shadow-md`}>
                        <h4 className={`text-xl font-semibold mb-3 ${data.color}`}>{data.title}</h4>
                        <p className={`mb-4 ${data.color}`}>{data.description}</p>
                        
                        {/* 해당 카테고리의 공개 정보 표시 */}
                        {data.disclosures.length > 0 && (
                          <div className="space-y-3">
                            <h5 className="font-medium text-gray-800 mb-2">공개 요구사항:</h5>
                            {data.disclosures.map((disclosure) => (
                              <div key={disclosure.id} className="bg-white p-3 rounded-md shadow-sm border border-gray-200">
                                <h6 className="font-semibold text-gray-800 mb-1">{disclosure.disclosure_id}</h6>
                                <p className="text-sm text-gray-700 mb-1">{disclosure.disclosure_summary}</p>
                                <p className="text-xs text-gray-500">{disclosure.disclosure_detail}</p>
                              </div>
                            ))}
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
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <h4 className="text-lg font-semibold text-green-900 mb-2">
                        📊 {companyFinancialData.company_name} TCFD 분석
                      </h4>
                      <p className="text-green-700">
                        회사 정보와 재무 데이터를 기반으로 TCFD 프레임워크에 따른 분석을 진행할 수 있습니다.
                      </p>
                    </div>
                  ) : (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                      <h4 className="text-lg font-semibold text-blue-900 mb-2">회사 검색이 필요합니다</h4>
                      <p className="text-blue-700 mb-4">
                        회사정보 탭에서 회사명을 검색하면 해당 회사의 TCFD 분석을 진행할 수 있습니다.
                      </p>
                      <button
                        onClick={() => setActiveTab(1)}
                        className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        회사정보 탭으로 이동
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* 탭 4: 기후시나리오 */}
          {activeTab === 4 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🌍 기후시나리오</h2>
              <div className="space-y-4">
                                 <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                   <h3 className="text-lg font-semibold text-red-900 mb-2">RCP 8.5 (고탄소 시나리오)</h3>
                   <p className="text-red-700 mb-4">2100년까지 4.9°C 온도 상승, 극단적인 기후 변화</p>
                   <button 
                     onClick={() => handleClimateDetails('ssp8.5')}
                     className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors text-sm"
                   >
                     상세보기
                   </button>
                 </div>
                 <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                   <h3 className="text-lg font-semibold text-blue-900 mb-2">RCP 2.6 (극저탄소 시나리오)</h3>
                   <p className="text-blue-700 mb-4">2100년까지 1.6°C 온도 상승, 파리협정 목표 달성</p>
                   <button 
                     onClick={() => handleClimateDetails('ssp2.6')}
                     className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                   >
                     상세보기
                   </button>
                 </div>
              </div>
            </div>
          )}

          {/* 탭 5: AI보고서 초안 */}
          {activeTab === 5 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">🤖 AI보고서 초안</h2>
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg border border-purple-200">
                <h3 className="text-lg font-semibold text-purple-900 mb-4">AI 기반 TCFD 보고서 생성</h3>
                <div className="space-y-3">
                  <div className="flex items-center">
                    <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                    <span className="text-purple-700">회사 정보 및 재무 데이터 분석</span>
                  </div>
                  <div className="flex items-center">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                    <span className="text-blue-700">기후 위험 평가 및 시나리오 분석</span>
                  </div>
                  <div className="flex items-center">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                    <span className="text-green-700">TCFD 프레임워크 기반 보고서 생성</span>
                  </div>
                  <div className="flex items-center">
                    <span className="w-2 h-2 bg-yellow-500 rounded-full mr-3"></span>
                    <span className="text-yellow-700">지속가능성 지표 및 권장사항 제시</span>
                  </div>
                </div>
                <button className="mt-6 px-6 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700">
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
     </div>
   );
 }
