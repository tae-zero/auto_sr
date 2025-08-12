import { create } from 'zustand';

interface AuthState {
  isAuthenticated: boolean;
  isInitialized: boolean;
  user: {
    username: string;
    email?: string;
  } | null;
  checkAuthStatus: () => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
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

  login: async (username: string, _password: string) => {
    try {
      // TODO: 실제 로그인 API 호출
      // 임시 로그인 로직
      const mockUserData = {
        username,
        email: `${username}@example.com`
      };
      
      localStorage.setItem('auth_token', 'mock_token');
      localStorage.setItem('user_data', JSON.stringify(mockUserData));

      set({ 
        isAuthenticated: true,
        user: mockUserData
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
  }
}));