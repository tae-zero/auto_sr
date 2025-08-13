'use client';

import { useState, useEffect } from 'react';

// 재무정보 타입 정의 (Frontend용)
interface FinancialData {
  revenue: number;
  total_assets: number;
  total_liabilities: number;
  total_equity: number;
  operating_income?: number;
  net_income?: number;
  fiscal_year: string;
  company_id: string;
}

// 회사 정보 타입
interface CompanyInfo {
  id: string;
  name: string;
  industry: string;
  size: string;
  location: string;
}

// 테이블 데이터 타입 정의
interface TableRecord {
  id: string;
  [key: string]: string | number | boolean;
}

// 6개 테이블 데이터 타입
interface CompanyFinancialData {
  company_name: string;
  company_id: string;
  total_records: number;
  tables: string[];
  data: {
    employee: TableRecord[];
    profit_loss: TableRecord[];
    executive: TableRecord[];
    financial_status: TableRecord[];
    corp: TableRecord[];
    all_corp: TableRecord[];
  };
}

export default function TcfdSrPage() {
  const [activeTab, setActiveTab] = useState(1);
  const [isLoadingFinancial, setIsLoadingFinancial] = useState(false);
  const [financialError, setFinancialError] = useState<string | null>(null);
  const [showFinancialAnalysis, setShowFinancialAnalysis] = useState(false);
  
  // 새로운 상태들
  const [companyName, setCompanyName] = useState('');
  const [companyFinancialData, setCompanyFinancialData] = useState<CompanyFinancialData | null>(null);
  const [isLoadingCompany, setIsLoadingCompany] = useState(false);
  const [companyError, setCompanyError] = useState<string | null>(null);
  const [availableCompanies, setAvailableCompanies] = useState<CompanyInfo[]>([]);

  // 회사 목록 로드
  const loadCompanies = async () => {
    try {
      const response = await fetch('/api/companies');
      if (!response.ok) {
        throw new Error(`회사 목록 로드 실패: ${response.status}`);
      }
      
      const data = await response.json();
      if (data.success === false) {
        throw new Error(data.error || '회사 목록을 불러올 수 없습니다');
      }
      
      setAvailableCompanies(data.companies || []);
    } catch (error) {
      console.error('회사 목록 로드 실패:', error);
      setCompanyError(error instanceof Error ? error.message : '알 수 없는 오류');
    }
  };

  // 회사별 재무정보 로드
  const loadCompanyFinancialData = async (companyName: string) => {
    if (!companyName.trim()) return;
    
    setIsLoadingCompany(true);
    setCompanyError(null);
    
    try {
      const response = await fetch(`/api/company-financial-data?company_name=${encodeURIComponent(companyName)}`);
      if (!response.ok) {
        throw new Error(`회사별 재무정보 로드 실패: ${response.status}`);
      }
      
      const data = await response.json();
      if (data.success === false) {
        throw new Error(data.error || '재무정보를 불러올 수 없습니다');
      }
      
      setCompanyFinancialData(data);
    } catch (error) {
      setCompanyError(error instanceof Error ? error.message : '알 수 없는 오류');
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

  // 재무 분석 실행
  const handleFinancialAnalysis = () => {
    setShowFinancialAnalysis(true);
  };

  // 컴포넌트 마운트 시 회사 목록 로드
  useEffect(() => {
    loadCompanies();
  }, []);

  // 재무정보 표시 컴포넌트
  const renderFinancialTable = (data: TableRecord[], title: string) => {
    if (!data || data.length === 0) {
      return (
        <div className="text-center py-4 text-gray-500">
          {title} 데이터가 없습니다
        </div>
      );
    }

    const columns = Object.keys(data[0] || {});

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
                      placeholder="회사명을 입력하세요 (예: 삼성전자, 현대자동차)"
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
                
                {/* 사용 가능한 회사 목록 */}
                {availableCompanies.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm text-gray-600 mb-2">사용 가능한 회사:</p>
                    <div className="flex flex-wrap gap-2">
                      {availableCompanies.map((company) => (
                        <button
                          key={company.id}
                          onClick={() => {
                            setCompanyName(company.name);
                            loadCompanyFinancialData(company.name);
                          }}
                          className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
                        >
                          {company.name}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* 회사별 재무정보 표시 */}
              {companyFinancialData && (
                <div className="mt-6">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <h3 className="text-lg font-semibold text-blue-900 mb-2">
                      📊 {companyFinancialData.company_name} 재무정보
                    </h3>
                    <p className="text-blue-700">
                      총 {companyFinancialData.total_records}개 레코드, 
                      {companyFinancialData.tables.join(', ')} 테이블
                    </p>
                  </div>

                  {/* 6개 테이블 데이터 표시 */}
                  {renderFinancialTable(companyFinancialData.data.employee, '직원 정보')}
                  {renderFinancialTable(companyFinancialData.data.profit_loss, '손익계산')}
                  {renderFinancialTable(companyFinancialData.data.executive, '임원 정보')}
                  {renderFinancialTable(companyFinancialData.data.financial_status, '재무상태')}
                  {renderFinancialTable(companyFinancialData.data.corp, '기업 정보')}
                  {renderFinancialTable(companyFinancialData.data.all_corp, '전체기업 정보')}
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
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-3">재무정보 입력</h3>
                  <button
                    // onClick={loadFinancialData} // This line was removed as per the edit hint
                    disabled={isLoadingFinancial}
                    className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isLoadingFinancial ? '로딩 중...' : '재무정보 불러오기'}
                  </button>
                </div>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-3">재무분석</h3>
                  <button
                    onClick={handleFinancialAnalysis}
                    className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    재무분석 실행
                  </button>
                </div>
              </div>

              {financialError && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-red-700">{financialError}</p>
                </div>
              )}

              {showFinancialAnalysis && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
                  <h3 className="text-lg font-semibold text-green-900 mb-2">재무분석 결과</h3>
                  <p className="text-green-700">
                    재무분석이 완료되었습니다. 상세 결과는 TCFD 프레임워크 탭에서 확인할 수 있습니다.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* 탭 3: TCFD 프레임워크 */}
          {activeTab === 3 && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">📊 TCFD 프레임워크</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">거버넌스</h3>
                  <p className="text-blue-700">기후 관련 위험과 기회에 대한 감독 및 책임</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">전략</h3>
                  <p className="text-green-700">기후 관련 위험과 기회가 비즈니스 모델에 미치는 영향</p>
                </div>
                <div className="bg-yellow-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">위험관리</h3>
                  <p className="text-yellow-700">기후 관련 위험 식별, 평가 및 관리</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold mb-2">지표 및 목표</h3>
                  <p className="text-purple-700">기후 관련 위험과 기회를 평가하고 관리하기 위한 지표 및 목표</p>
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
                  <p className="text-red-700">2100년까지 4.9°C 온도 상승, 극단적인 기후 변화</p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg border border-orange-200">
                  <h3 className="text-lg font-semibold text-orange-900 mb-2">RCP 6.0 (중간 시나리오)</h3>
                  <p className="text-orange-700">2100년까지 3.0°C 온도 상승, 적극적인 기후 정책</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <h3 className="text-lg font-semibold text-green-900 mb-2">RCP 4.5 (저탄소 시나리오)</h3>
                  <p className="text-green-700">2100년까지 2.4°C 온도 상승, 강력한 기후 정책</p>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <h3 className="text-lg font-semibold text-blue-900 mb-2">RCP 2.6 (극저탄소 시나리오)</h3>
                  <p className="text-blue-700">2100년까지 1.6°C 온도 상승, 파리협정 목표 달성</p>
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
    </div>
  );
}
