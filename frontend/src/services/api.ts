import axios from 'axios';

// 타입 정의
interface SignupData {
  company_id: string;
  industry: string;
  email: string;
  name: string;
  age: string;
  auth_id: string;
  auth_pw: string;
}

interface LoginData {
  auth_id: string;
  auth_pw: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  message: string;
  chat_history?: ChatMessage[];
}

interface AuthResponse {
  success: boolean;
  message: string;
  email?: string;
  user_id?: string;
  name?: string;
  company_id?: string;
}

// API 기본 설정
const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL || 'http://localhost:8008';
const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8080';
const CHATBOT_URL = process.env.NEXT_PUBLIC_CHATBOT_URL || 'http://localhost:8006';

// API 클라이언트 설정
export const apiClient = axios.create({
  baseURL: GATEWAY_URL, // Gateway를 기본 URL로 설정
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth Service API
export const authAPI = {
  // Gateway를 통한 인증
  signup: (data: SignupData): Promise<{ data: AuthResponse }> => apiClient.post('/api/v1/auth/signup', data),
  login: (data: LoginData): Promise<{ data: AuthResponse }> => apiClient.post('/api/v1/auth/login', data),
  
  // 직접 auth-service 연결 (백업용)
  signupDirect: (data: SignupData): Promise<{ data: AuthResponse }> => axios.post(`${AUTH_URL}/signup`, data),
  loginDirect: (data: LoginData): Promise<{ data: AuthResponse }> => axios.post(`${AUTH_URL}/login`, data),
};

// Chatbot Service API
export const chatbotAPI = {
  // 챗봇 서비스 상태 확인
  healthCheck: () => axios.get(`${CHATBOT_URL}/health`),
  
  // 챗봇 대화
  chat: (message: string, chatHistory: ChatMessage[] = []) => {
    const formData = new FormData();
    formData.append('message', message);
    formData.append('chat_history', JSON.stringify(chatHistory));
    
    return axios.post(`${CHATBOT_URL}/chat`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// AI Service API
export const aiApi = {
  // AI 서비스 상태 확인
  healthCheck: () => apiClient.get('/api/v1/ai/health'),
  
  // AI 챗봇 대화
  chat: (message: string, chatHistory: ChatMessage[] = []) => {
    const formData = new FormData();
    formData.append('message', message);
    formData.append('chat_history', JSON.stringify(chatHistory));
    
    return apiClient.post('/api/v1/ai/chat', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 문서 업로드
  uploadDocument: (file: File, description: string) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', description);
    
    return apiClient.post('/api/v1/ai/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

// GRI Report 생성 데이터 타입
interface GRIReportData {
  company_name: string;
  report_title: string;
  report_content: string;
  status?: string;
}

// Materiality 분석 생성 데이터 타입
interface MaterialityAnalysisData {
  company_name: string;
  analysis_title: string;
  stakeholder_impact: number;
  business_impact: number;
  priority_score: number;
  analysis_content: string;
  status?: string;
}

// GRI Service API
export const griAPI = {
  healthCheck: () => apiClient.get('/api/v1/gri/health'),
  getReports: (token: string) => apiClient.get('/api/v1/gri/reports', {
    headers: { 'Authorization': `Bearer ${token}` }
  }),
  createReport: (data: GRIReportData, token: string) => apiClient.post('/api/v1/gri/reports', data, {
    headers: { 'Authorization': `Bearer ${token}` }
  }),
  signup: (data: SignupData): Promise<{ data: AuthResponse }> => apiClient.post('/api/v1/gri/auth/signup', data),
  login: (data: LoginData): Promise<{ data: AuthResponse }> => apiClient.post('/api/v1/gri/auth/login', data),
};

// Materiality Service API
export const materialityAPI = {
  healthCheck: () => apiClient.get('/api/v1/materiality/health'),
  getAnalyses: (token: string) => apiClient.get('/api/v1/materiality/analyses', {
    headers: { 'Authorization': `Bearer ${token}` }
  }),
  createAnalysis: (data: MaterialityAnalysisData, token: string) => apiClient.post('/api/v1/materiality/analyses', data, {
    headers: { 'Authorization': `Bearer ${token}` }
  }),
  signup: (data: SignupData): Promise<{ data: AuthResponse }> => apiClient.post('/api/v1/materiality/auth/signup', data),
  login: (data: LoginData): Promise<{ data: AuthResponse }> => apiClient.post('/api/v1/materiality/auth/login', data),
};

// TCFD Service API
export const tcfdAPI = {
  healthCheck: () => apiClient.get('/api/v1/tcfd/health'),
  getCompanyFinancialData: (companyName: string) => apiClient.get(`/api/v1/tcfd/company-financial-data?company_name=${encodeURIComponent(companyName)}`),
  getCompanyFinancialSummary: (companyName: string) => apiClient.get(`/api/v1/tcfd/company-financial-summary?company_name=${encodeURIComponent(companyName)}`),
  getAllCompanies: () => apiClient.get('/api/v1/tcfd/companies'),
  getFinancialData: () => apiClient.get('/api/v1/tcfd/financial-data'),
  createFinancialData: (data: Record<string, unknown>) => apiClient.post('/api/v1/tcfd/financial-data', data),
  getClimateScenarios: () => apiClient.get('/api/v1/tcfd/climate-scenarios'),
  // TCFD 표준 정보 조회 추가
  getTcfdStandards: () => apiClient.get('/api/v1/tcfd/standards'),
  getTcfdStandardsByCategory: (category: string) => apiClient.get(`/api/v1/tcfd/standards/${category}`),
};

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    // 토큰이 있다면 헤더에 추가
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 401 에러 시 토큰 제거
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
    }
    return Promise.reject(error);
  }
);

export default apiClient; 