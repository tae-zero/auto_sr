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
  message: string;
  chat_history?: any[];
}

interface DocumentUpload {
  file: File;
  description: string;
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
  signup: (data: SignupData) => apiClient.post('/auth/signup', data),
  login: (data: LoginData) => apiClient.post('/auth/login', data),
  
  // 직접 auth-service 연결 (백업용)
  signupDirect: (data: SignupData) => axios.post(`${AUTH_URL}/signup`, data),
  loginDirect: (data: LoginData) => axios.post(`${AUTH_URL}/login`, data),
};

// Chatbot Service API
export const chatbotAPI = {
  // 챗봇 서비스 상태 확인
  healthCheck: () => axios.get(`${CHATBOT_URL}/health`),
  
  // 챗봇 대화
  chat: (message: string, chatHistory: any[] = []) => {
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
  chat: (message: string, chatHistory: any[] = []) => {
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
    
    return apiClient.post('/api/v1/ai/upload-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 벡터 검색
  search: (query: string, topK: number = 5) => 
    apiClient.get(`/api/v1/ai/search?query=${encodeURIComponent(query)}&top_k=${topK}`),
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