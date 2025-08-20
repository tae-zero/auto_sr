'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/Header';
import { authService } from '@/services/authService';

interface MaterialityData {
  id: number;
  created_at: string;
  esg_division?: string;
  materiality_list?: string;
  environment?: string;
  social?: string;
  governance?: string;
  industry?: string;
  disclosure_topic?: string;
  kpi_category_e?: string;
  kpi_category_s?: string;
  kpi_category_g?: string;
  index_name?: string;
  [key: string]: string | number | undefined;
}



export default function MaterialityPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const [data, setData] = useState<{
    categories: MaterialityData[];
    kcgs: MaterialityData[];
    sasb: MaterialityData[];
    sustainbestE: MaterialityData[];
    sustainbestS: MaterialityData[];
    sustainbestG: MaterialityData[];
  }>({
    categories: [],
    kcgs: [],
    sasb: [],
    sustainbestE: [],
    sustainbestS: [],
    sustainbestG: []
  });

  const router = useRouter();

  const tabs = [
    { 
      name: '카테고리', 
      key: 'categories'
    },
    { 
      name: 'KCGS', 
      key: 'kcgs'
    },
    { 
      name: 'SASB', 
      key: 'sasb'
    },
    { 
      name: '서스틴베스트 E', 
      key: 'sustainbestE'
    },
    { 
      name: '서스틴베스트 S', 
      key: 'sustainbestS'
    },
    { 
      name: '서스틴베스트 G', 
      key: 'sustainbestG'
    }
  ];

  // 인증 상태 확인
  useEffect(() => {
    if (!authService.isAuthenticated()) {
      setError('로그인이 필요합니다.');
      router.push('/login');
      return;
    }
    
    setIsAuthenticated(true);
    fetchAllMaterialityData();
  }, [router]);

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

  const fetchAllMaterialityData = async () => {
    try {
      setLoading(true);
      
      // Materiality Service 직접 호출 (통합 인증 서비스 사용)
      const API_BASE_URL = process.env.NEXT_PUBLIC_MATERIALITY_URL || 'https://materiality-service-production-9a40.up.railway.app';
      
      console.log('API 호출 시작:', API_BASE_URL);
      console.log('통합 인증 서비스로 API 호출 시도');
  
      // Materiality Service 직접 호출
      const endpoints = [
        '/api/v1/materiality/data/categories',
        '/api/v1/materiality/data/kcgs',
        '/api/v1/materiality/data/sasb',
        '/api/v1/materiality/data/sustainbest-e',
        '/api/v1/materiality/data/sustainbest-s',
        '/api/v1/materiality/data/sustainbest-g'
      ];
  
      const responses = await Promise.all(
        endpoints.map(async (endpoint) => {
          console.log(`${endpoint} 호출 중...`);
          // 통합 인증 서비스의 authenticatedFetch 사용
          return await authService.authenticatedFetch(`${API_BASE_URL}${endpoint}`);
        })
      );

      console.log('API 응답 상태:', responses.map(r => r.status));

      const results = await Promise.all(
        responses.map(response => response.json())
      );

      console.log('API 응답 데이터:', results);

      setData({
        categories: results[0].data || [],
        kcgs: results[1].data || [],
        sasb: results[2].data || [],
        sustainbestE: results[3].data || [],
        sustainbestS: results[4].data || [],
        sustainbestG: results[5].data || []
      });
    } catch (err) {
      console.error('API 호출 오류 상세:', err);
      if (err instanceof Error && err.message.includes('인증')) {
        setError(err.message);
      } else {
        setError('데이터를 불러오는 중 오류가 발생했습니다.');
      }
      
      // 오류 발생 시에도 기본 UI를 보여주기 위해 더미 데이터 설정
      setData({
        categories: [{ id: 1, esg_division: '환경', materiality_list: '테스트 데이터', created_at: new Date().toISOString() }],
        kcgs: [{ id: 1, environment: '테스트', social: '테스트', governance: '테스트', created_at: new Date().toISOString() }],
        sasb: [{ id: 1, industry: '테스트', disclosure_topic: '테스트', created_at: new Date().toISOString() }],
        sustainbestE: [{ id: 1, kpi_category_e: '테스트', index_name: '테스트', created_at: new Date().toISOString() }],
        sustainbestS: [{ id: 1, kpi_category_s: '테스트', index_name: '테스트', created_at: new Date().toISOString() }],
        sustainbestG: [{ id: 1, kpi_category_g: '테스트', index_name: '테스트', created_at: new Date().toISOString() }]
      });
    } finally {
      setLoading(false);
    }
  };



  const renderTable = (tableData: Record<string, string | number>[], columns: string[]) => {
    if (!tableData || tableData.length === 0) {
      return (
        <div className="text-center py-8 text-gray-500">
          데이터가 없습니다.
        </div>
      );
    }

    return (
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-gray-200 rounded-lg shadow-sm">
          <thead className="bg-gray-50">
            <tr>
              {columns.map((column, index) => (
                <th
                  key={index}
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider border-b"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {tableData.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {columns.map((column, colIndex) => (
                  <td
                    key={colIndex}
                    className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 border-b"
                  >
                    {row[column] || '-'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const getTableColumns = (tabKey: string) => {
    switch (tabKey) {
      case 'categories':
        return ['ID', 'ESG 구분', '중대성평가 목록', '생성일'];
      case 'kcgs':
        return ['ID', '환경(E)', '사회(S)', '거버넌스(G)', '생성일'];
      case 'sasb':
        return ['ID', '산업', '공시 주제', '생성일'];
      case 'sustainbestE':
        return ['ID', 'KPI 카테고리 E', '인덱스명', '생성일'];
      case 'sustainbestS':
        return ['ID', 'KPI 카테고리 S', '인덱스명', '생성일'];
      case 'sustainbestG':
        return ['ID', 'KPI 카테고리 G', '인덱스명', '생성일'];
      default:
        return [];
    }
  };

  const getTableData = (tabKey: string) => {
    const tableData = data[tabKey as keyof typeof data] || [];
    const columns = getTableColumns(tabKey);
    
    return tableData.map(row => {
      const mappedRow: Record<string, string | number> = {};
      columns.forEach(column => {
        switch (column) {
          case 'ID':
            mappedRow[column] = row.id;
            break;
          case 'ESG 구분':
            mappedRow[column] = row.esg_division || '-';
            break;
          case '중대성평가 목록':
            mappedRow[column] = row.materiality_list || '-';
            break;
          case '환경(E)':
            mappedRow[column] = row.environment || '-';
            break;
          case '사회(S)':
            mappedRow[column] = row.social || '-';
            break;
          case '거버넌스(G)':
            mappedRow[column] = row.governance || '-';
            break;
          case '산업':
            mappedRow[column] = row.industry || '-';
            break;
          case '공시 주제':
            mappedRow[column] = row.disclosure_topic || '-';
            break;
          case 'KPI 카테고리 E':
            mappedRow[column] = row.kpi_category_e || '-';
            break;
          case 'KPI 카테고리 S':
            mappedRow[column] = row.kpi_category_s || '-';
            break;
          case 'KPI 카테고리 G':
            mappedRow[column] = row.kpi_category_g || '-';
            break;
          case '인덱스명':
            mappedRow[column] = row.index_name || '-';
            break;
          case '생성일':
            mappedRow[column] = row.created_at ? new Date(row.created_at).toLocaleDateString('ko-KR') : '-';
            break;
          default:
            mappedRow[column] = (row[column.toLowerCase() as keyof MaterialityData] as string) || '-';
        }
      });
      return mappedRow;
    });
  };



  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header />
        <div className="pt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">데이터를 불러오는 중...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header />
        <div className="pt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center">
              <div className="text-red-600 text-lg mb-4">⚠️ {error}</div>
              <button
                onClick={fetchAllMaterialityData}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                다시 시도
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Header />
      <div className="pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 헤더 */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Materiality 분석
            </h1>
            <p className="text-xl text-gray-600">
              핵심 이슈를 파악하기 위한 6개 테이블 데이터
            </p>
          </div>

          {/* 탭 네비게이션 */}
          <div className="mb-8">
            <nav className="flex space-x-8 justify-center">
              {tabs.map((tab, index) => (
                <button
                  key={tab.key}
                  onClick={() => {
                    console.log('탭 클릭:', tab.name, index);
                    setActiveTab(index);
                  }}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                    activeTab === index
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* 데이터 테이블 */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  {tabs[activeTab].name} 데이터
                </h2>
                <p className="text-gray-600">
                  총 {getTableData(tabs[activeTab].key).length}개의 항목
                </p>
              </div>
              

            </div>
            
            {renderTable(
              getTableData(tabs[activeTab].key),
              getTableColumns(tabs[activeTab].key)
            )}
          </div>
        </div>
      </div>


    </div>
  );
}
