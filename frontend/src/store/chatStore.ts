import { create } from 'zustand';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  addMessage: (content: string, role: 'user' | 'assistant') => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  
  addMessage: (content: string, role: 'user' | 'assistant') => 
    set((state) => ({
      messages: [...state.messages, {
        id: Date.now().toString(),
        content,
        role,
        timestamp: new Date(),
      }],
    })),
    
  setLoading: (loading: boolean) => set({ isLoading: loading }),
  
  clearMessages: () => set({ messages: [] }),
})); 