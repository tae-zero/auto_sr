import api from './api';

export interface ChatResponse {
  message: string;
  timestamp: string;
}

export interface ChatHistoryItem {
  id: string;
  content: string;
  role: string;
  timestamp: string;
}

export const chatService = {
  // 메시지 전송 (gateway를 통해 chat-service로 전달)
  sendMessage: async (message: string): Promise<ChatResponse> => {
    try {
      const response = await api.post('/chat-service/chat', { message });
      return response.data;
    } catch (error) {
      console.error('채팅 메시지 전송 오류:', error);
      throw error;
    }
  },

  // 채팅 히스토리 가져오기
  getChatHistory: async (): Promise<ChatHistoryItem[]> => {
    try {
      const response = await api.get('/chat-service/chat/history');
      return response.data;
    } catch (error) {
      console.error('채팅 히스토리 가져오기 오류:', error);
      throw error;
    }
  },

  // 채팅 히스토리 삭제
  clearChatHistory: async (): Promise<void> => {
    try {
      await api.delete('/chat-service/chat/history');
    } catch (error) {
      console.error('채팅 히스토리 삭제 오류:', error);
      throw error;
    }
  },
}; 