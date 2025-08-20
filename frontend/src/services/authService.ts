// 통합 인증 서비스
export class AuthService {
  private static instance: AuthService;
  private token: string | null = null;

  private constructor() {
    this.token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
  }

  public static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  // 토큰 설정
  public setToken(token: string, rememberMe: boolean = false): void {
    this.token = token;
    if (rememberMe) {
      localStorage.setItem('authToken', token);
    } else {
      sessionStorage.setItem('authToken', token);
    }
  }

  // 토큰 가져오기
  public getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
    }
    return this.token;
  }

  // 토큰 제거
  public removeToken(): void {
    this.token = null;
    localStorage.removeItem('authToken');
    sessionStorage.removeItem('authToken');
  }

  // 인증된 사용자 여부 확인
  public isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // API 호출용 헤더 생성
  public getAuthHeaders(): Record<string, string> {
    const token = this.getToken();
    if (!token) {
      throw new Error('인증 토큰이 없습니다. 로그인이 필요합니다.');
    }

    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  }

  // API 호출 래퍼 (인증 포함)
  public async authenticatedFetch(url: string, options: RequestInit = {}): Promise<Response> {
    const headers = this.getAuthHeaders();
    
    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...options.headers
      }
    });

    // 인증 실패 시 처리
    if (response.status === 401) {
      this.removeToken();
      window.location.href = '/login';
      throw new Error('인증이 만료되었습니다. 다시 로그인해주세요.');
    }

    return response;
  }

  // 로그아웃
  public logout(): void {
    this.removeToken();
    window.location.href = '/login';
  }
}

// 싱글톤 인스턴스 내보내기
export const authService = AuthService.getInstance();
