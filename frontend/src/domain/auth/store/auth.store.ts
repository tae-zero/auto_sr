import { create } from 'zustand';

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
  login: (username: string, userData?: UserData) => Promise<void>;
  logout: () => Promise<void>;
  setUserData: (userData: UserData) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  isInitialized: false,
  user: null,

  checkAuthStatus: async () => {
    try {
      // TODO: API 호출로 실제 인증 상태 확인
      // 임시로 localStorage에서 토큰 확인
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
    } catch (error) {
      console.error('인증 상태 확인 중 오류:', error);
      set({ 
        isAuthenticated: false, 
        isInitialized: true,
        user: null
      });
    }
  },

  login: async (username: string, userData?: UserData) => {
    try {
      // 서버에서 받은 사용자 데이터가 있으면 사용, 없으면 기본값 사용
      const finalUserData: UserData = userData || {
        username,
        email: `${username}@example.com`
      };
      
      localStorage.setItem('auth_token', 'mock_token');
      localStorage.setItem('user_data', JSON.stringify(finalUserData));

      set({ 
        isAuthenticated: true,
        user: finalUserData
      });
    } catch (error) {
      console.error('로그인 중 오류:', error);
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