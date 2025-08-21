import { create } from 'zustand';
import apiClient from '../lib/api';

// 사용자 데이터 타입 정의
interface UserData {
  username: string;
  email?: string;
  name?: string;
  company_id?: string;
}

interface AuthState {
  isAuthenticated: boolean;
  isInitialized: boolean;
  user: UserData | null;
  checkAuthStatus: () => Promise<void>;
  login: (username: string, userData?: UserData, token?: string) => Promise<void>;
  logout: () => Promise<void>;
  setUserData: (userData: UserData) => void;
  refreshToken: () => Promise<boolean>;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  isInitialized: false,
  user: null,

  refreshToken: async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (!token) {
        return false;
      }

      // 토큰 갱신 API 호출
      const response = await apiClient.post('/api/v1/auth/refresh', {}, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.data.access_token) {
        localStorage.setItem('auth_token', response.data.access_token);
        return true;
      }
      return false;
    } catch (error) {
      console.error('토큰 갱신 중 오류:', error);
      return false;
    }
  },

  checkAuthStatus: async () => {
    try {
      const token = localStorage.getItem('auth_token');
      const userData = localStorage.getItem('user_data');

      if (token && userData) {
        // 토큰 유효성 검사 API 호출
        try {
          await apiClient.get('/api/v1/auth/verify');
          set({ 
            isAuthenticated: true, 
            isInitialized: true,
            user: JSON.parse(userData)
          });
        } catch (error: any) {
          // 401 에러인 경우에만 토큰 갱신 시도
          if (error.response?.status === 401) {
            // 토큰이 만료되었다면 갱신 시도
            const refreshed = await useAuthStore.getState().refreshToken();
            if (!refreshed) {
              // 갱신 실패시에만 로그아웃
              await useAuthStore.getState().logout();
            }
          } else {
            // 네트워크 오류 등은 인증 상태 유지
            console.log('⚠️ 네트워크 오류로 인한 인증 확인 실패, 인증 상태 유지');
            set({ 
              isAuthenticated: true, 
              isInitialized: true,
              user: JSON.parse(userData)
            });
          }
        }
      } else {
        set({ 
          isAuthenticated: false, 
          isInitialized: true,
          user: null
        });
      }
    } catch (error) {
      console.error('인증 상태 확인 중 오류:', error);
      // 네트워크 오류 등으로 인한 실패는 기존 인증 상태 유지
      const token = localStorage.getItem('auth_token');
      const userData = localStorage.getItem('user_data');
      
      if (token && userData) {
        set({ 
          isAuthenticated: true, 
          isInitialized: true,
          user: JSON.parse(userData)
        });
      } else {
        set({ 
          isAuthenticated: false, 
          isInitialized: true,
          user: null
        });
      }
    }
  },

  login: async (username: string, userData?: UserData, token?: string) => {
    try {
      // 서버에서 받은 사용자 데이터가 있으면 사용, 없으면 기본값 사용
      const finalUserData: UserData = userData || {
        username,
        email: `${username}@example.com`
      };
      
      localStorage.setItem('auth_token', token || 'mock_token');
      localStorage.setItem('user_data', JSON.stringify(finalUserData));

      set({ 
        isAuthenticated: true,
        user: finalUserData
      });
    } catch (error) {
      console.error('로그인 중 오류가 발생했습니다.');
      throw error;
    }
  },

  logout: async () => {
    try {
      // TODO: 실제 로그아웃 API 호출
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');

      set({ 
        isAuthenticated: false,
        user: null
      });
    } catch (error) {
      console.error('로그아웃 중 오류:', error);
      throw error;
    }
  },

  setUserData: (userData: UserData) => {
    set({ user: userData });
    localStorage.setItem('user_data', JSON.stringify(userData));
  }
}));
