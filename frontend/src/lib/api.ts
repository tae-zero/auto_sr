import axios from 'axios';

// MSA Gateway API 클라이언트
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// axios 인스턴스 생성
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 (로깅용)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 (로깅용)
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Gateway API 함수들
export const gatewayAPI = {
  // Gateway 상태 확인
  getStatus: () => apiClient.get('/'),
  
  // Gateway 헬스 체크
  getHealth: () => apiClient.get('/health'),
  
  // 서비스 목록 조회
  getServices: () => apiClient.get('/services'),
  
  // 특정 서비스 헬스 체크
  getServiceHealth: (serviceName: string) => 
    apiClient.get(`/services/${serviceName}/health`),
  
  // 프록시 요청 (서비스로 요청 전달)
  proxyRequest: (serviceName: string, path: string, method: string = 'GET', data?: any) => {
    const config = {
      method,
      url: `/${serviceName}/${path}`,
      ...(data && { data }),
    };
    return apiClient(config);
  },
};

// 서비스별 API 함수들
export const userAPI = {
  getUsers: () => gatewayAPI.proxyRequest('user-service', 'users'),
  getUser: (id: string) => gatewayAPI.proxyRequest('user-service', `users/${id}`),
  createUser: (userData: any) => gatewayAPI.proxyRequest('user-service', 'users', 'POST', userData),
  updateUser: (id: string, userData: any) => gatewayAPI.proxyRequest('user-service', `users/${id}`, 'PUT', userData),
  deleteUser: (id: string) => gatewayAPI.proxyRequest('user-service', `users/${id}`, 'DELETE'),
};

export const orderAPI = {
  getOrders: () => gatewayAPI.proxyRequest('order-service', 'orders'),
  getOrder: (id: string) => gatewayAPI.proxyRequest('order-service', `orders/${id}`),
  createOrder: (orderData: any) => gatewayAPI.proxyRequest('order-service', 'orders', 'POST', orderData),
  updateOrder: (id: string, orderData: any) => gatewayAPI.proxyRequest('order-service', `orders/${id}`, 'PUT', orderData),
  deleteOrder: (id: string) => gatewayAPI.proxyRequest('order-service', `orders/${id}`, 'DELETE'),
};

export const productAPI = {
  getProducts: () => gatewayAPI.proxyRequest('product-service', 'products'),
  getProduct: (id: string) => gatewayAPI.proxyRequest('product-service', `products/${id}`),
  createProduct: (productData: any) => gatewayAPI.proxyRequest('product-service', 'products', 'POST', productData),
  updateProduct: (id: string, productData: any) => gatewayAPI.proxyRequest('product-service', `products/${id}`, 'PUT', productData),
  deleteProduct: (id: string) => gatewayAPI.proxyRequest('product-service', `products/${id}`, 'DELETE'),
}; 