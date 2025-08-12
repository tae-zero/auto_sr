import axios from 'axios';

// 환경변수에서 API URL 가져오기
const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8080';
const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL || 'http://localhost:8008';
const CHATBOT_URL = process.env.NEXT_PUBLIC_CHATBOT_URL || 'http://localhost:8006';

const api = axios.create({
  baseURL: GATEWAY_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Auth Service API
export const authApi = axios.create({
  baseURL: AUTH_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chatbot Service API
export const chatbotApi = axios.create({
  baseURL: CHATBOT_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// AI Service API (Gateway를 통해)
export const aiApi = {
  // AI 서비스 상태 확인
  healthCheck: () => api.get('/api/v1/ai/health'),
  
  // AI 챗봇 대화
  chat: (message: string, chatHistory: unknown[] = []) => {
    const formData = new FormData();
    formData.append('message', message);
    formData.append('chat_history', JSON.stringify(chatHistory));
    
    return api.post('/api/v1/ai/chat', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 문서 업로드
  uploadDocument: (file: File, description: string = '') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('description', description);
    
    return api.post('/api/v1/ai/upload-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // 벡터 검색
  search: (query: string, topK: number = 5) => 
    api.get(`/api/v1/ai/search?query=${encodeURIComponent(query)}&top_k=${topK}`),
};

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    // 토큰이 있다면 헤더에 추가
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // 인증 오류 처리
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api; 