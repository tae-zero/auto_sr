import axios from 'axios';
import { useAuthStore } from '../state/auth.store';

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
  token?: string;
  email?: string;
  name?: string;
  company_id?: string;
  user_id?: string | number;
  error?: string | null;
  timestamp?: string | null;
}

// API 기본 설정
const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL || 'http://auth-service:8008';
const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://gateway:8080';
const CHATBOT_URL = process.env.NEXT_PUBLIC_CHATBOT_URL || 'http://chatbot-service:8001';
const LLM_SERVICE_URL = process.env.NEXT_PUBLIC_LLM_SERVICE_URL || 'http://localhost:8002';

// 환경변수 검증
if (!process.env.NEXT_PUBLIC_GATEWAY_URL) {
  console.warn('⚠️ NEXT_PUBLIC_GATEWAY_URL이 설정되지 않았습니다. 기본값을 사용합니다.');
}

if (!process.env.NEXT_PUBLIC_LLM_SERVICE_URL) {
  console.warn('⚠️ NEXT_PUBLIC_LLM_SERVICE_URL이 설정되지 않았습니다. 기본값을 사용합니다.');
}

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

// TCFD Service API (Gateway를 통한 요청)
export const tcfdAPI = {
  healthCheck: () => apiClient.get('/api/v1/tcfd/health'),
  getCompanyFinancialData: (companyName: string) => apiClient.get(`/api/v1/tcfd/company-financial-data?company_name=${encodeURIComponent(companyName)}`),
  getCompanyFinancialSummary: (companyName: string) => apiClient.get(`/api/v1/tcfd/company-financial-summary?company_name=${encodeURIComponent(companyName)}`),
  getCompanyOverview: (companyName: string) => {
    const token = localStorage.getItem('auth_token');
    return apiClient.get(`/api/v1/tcfd/company-overview?company_name=${encodeURIComponent(companyName)}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  },
  getAllCompanies: () => apiClient.get('/api/v1/tcfd/companies'),
  getFinancialData: () => apiClient.get('/api/v1/tcfd/financial-data'),
  createFinancialData: (data: Record<string, unknown>) => apiClient.post('/api/v1/tcfd/financial-data', data),
  getClimateScenarios: () => apiClient.get('/api/v1/tcfd/climate-scenarios'),
  // TCFD 표준 정보 조회 추가
  getTcfdStandards: () => {
    const token = localStorage.getItem('auth_token');
    return apiClient.get('/api/v1/tcfd/standards', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  },
  getTcfdStandardsByCategory: (category: string) => apiClient.get(`/api/v1/tcfd/standards/${category}`),
};

// TCFD 입력 데이터 타입
interface TCFDInputData {
  company_name: string;
  user_id?: string;
  governance_g1?: string;
  governance_g2?: string;
  strategy_s1?: string;
  strategy_s2?: string;
  strategy_s3?: string;
  risk_management_r1?: string;
  risk_management_r2?: string;
  metrics_targets_m1?: string;
  metrics_targets_m2?: string;
  metrics_targets_m3?: string;
}

// TCFD Report Service API (Gateway를 통한 요청)
export const tcfdReportAPI = {
  healthCheck: () => apiClient.get('/api/v1/tcfdreport/health'),
  getCompanyFinancialData: (companyName: string) => apiClient.get(`/api/v1/tcfdreport/company-financial-data?company_name=${encodeURIComponent(companyName)}`),
  getTcfdStandards: () => apiClient.get('/api/v1/tcfdreport/standards'),
  // TCFD 입력 데이터 관련 API
  createTcfdInput: (data: TCFDInputData) => apiClient.post('/api/v1/tcfdreport/inputs', data),
  getTcfdInputs: () => apiClient.get('/api/v1/tcfdreport/inputs'),
};

// LLM Service API (TCFD 보고서 생성용)
export const llmServiceAPI = {
  // TCFD 보고서 초안 생성 (Gateway를 통한 통합 호출)
  generateTCFDReport: async (tcfdInputs: TCFDInputs) => {
    const response = await fetch('/api/llm/generate-tcfd-report', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: `TCFD 보고서 생성을 위한 질문: ${JSON.stringify(tcfdInputs)}`,
        sections: [
          '기후 관련 위험 평가',
          '기후 관련 기회 평가', 
          '기후 관련 목표 설정',
          '기후 관련 전략 및 계획'
        ],
        top_k: 8
      })
    });
    return response.json();
  },

  // OpenAI RAG로 초안 생성 (직접 LLM Service 호출)
  generateOpenAIRAG: async (tcfdInputs: TCFDInputs) => {
    const response = await fetch('/api/llm/generate-openai-rag', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: `TCFD 보고서 생성을 위한 질문: ${JSON.stringify(tcfdInputs)}`,
        sections: [
          '기후 관련 위험 평가',
          '기후 관련 기회 평가',
          '기후 관련 목표 설정',
          '기후 관련 전략 및 계획'
        ],
        top_k: 8
      })
    });
    return response.json();
  },

  // Hugging Face RAG로 초안 생성 (직접 LLM Service 호출)
  generateHFRAG: async (tcfdInputs: TCFDInputs) => {
    const response = await fetch('/api/llm/generate-hf-rag', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: `TCFD 보고서 생성을 위한 질문: ${JSON.stringify(tcfdInputs)}`,
        sections: [
          '기후 관련 위험 평가',
          '기후 관련 기회 평가',
          '기후 관련 목표 설정',
          '기후 관련 전략 및 계획'
        ],
        top_k: 8
      })
    });
    return response.json();
  },

  // TCFD 권고사항별 문장 생성 (OpenAI)
  generateTCFDRecommendationOpenAI: async (companyName: string, recommendationType: string, userInput: string) => {
    const response = await fetch('/api/llm/generate-tcfd-recommendation-openai', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_name: companyName,
        recommendation_type: recommendationType,
        user_input: userInput,
        llm_provider: 'openai'
      })
    });
    return response.json();
  },

  // TCFD 권고사항별 문장 생성 (KoAlpaca)
  generateTCFDRecommendationKoAlpaca: async (companyName: string, recommendationType: string, userInput: string) => {
    const response = await fetch('/api/llm/generate-tcfd-recommendation-koalpaca', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_name: companyName,
        recommendation_type: recommendationType,
        user_input: userInput,
        llm_provider: 'huggingface'
      })
    });
    return response.json();
  }
};

// TCFD 입력 데이터 타입 (LLM Service용)
interface TCFDInputs {
  m1: string;
  m2: string;
  m3: string;
}

// 요청 인터셉터
apiClient.interceptors.request.use(
  async (config) => {
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
  async (error) => {
    const originalRequest = error.config;

    // 401 에러이고 토큰 갱신을 시도하지 않은 요청인 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // 토큰 갱신 시도
        const refreshed = await useAuthStore.getState().refreshToken();
        if (refreshed) {
          // 토큰 갱신 성공시 원래 요청 재시도
          const token = localStorage.getItem('auth_token');
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        console.error('토큰 갱신 실패:', refreshError);
      }

      // 토큰 갱신 실패시에만 로그아웃 (네트워크 오류 등은 제외)
      if (error.response?.status === 401) {
        await useAuthStore.getState().logout();
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient; 
