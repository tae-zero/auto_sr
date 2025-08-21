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

      if (response.data.token) {
        localStorage.setItem('auth_token', response.data.token);
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
        } catch (error) {
          // 토큰이 만료되었다면 갱신 시도
          const refreshed = await useAuthStore.getState().refreshToken();
          if (!refreshed) {
            // 갱신 실패시 로그아웃
            await useAuthStore.getState().logout();
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
      set({ 
        isAuthenticated: false, 
        isInitialized: true,
        user: null
      });
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
