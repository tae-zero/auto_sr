'use client';

import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '@/store/chatStore';
import { chatService } from '@/services/chatService';

export default function Home() {
  const [inputValue, setInputValue] = useState('');
  const [jsonData, setJsonData] = useState<any>(null);
  const { messages, isLoading, addMessage, setLoading } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    
    // 입력된 텍스트를 JSON으로 변환
    try {
      const jsonObject = {
        message: userMessage,
        timestamp: new Date().toISOString(),
        id: Date.now().toString(),
        type: 'user_input'
      };
      
      setJsonData(jsonObject);
      
      // POST 방식으로 입력된 값을 alert 창에 표시
      alert(`POST 요청으로 전송된 메시지: ${userMessage}\n\nJSON 데이터:\n${JSON.stringify(jsonObject, null, 2)}`);
      
    } catch (error) {
      alert('JSON 변환 중 오류가 발생했습니다.');
      return;
    }
    
    setInputValue('');
    addMessage(userMessage, 'user');
    setLoading(true);

    try {
      const response = await chatService.sendMessage(userMessage);
      addMessage(response.message, 'assistant');
    } catch (error) {
      addMessage('죄송합니다. 오류가 발생했습니다. 다시 시도해주세요.', 'assistant');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex flex-col">
      {/* 헤더 */}
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <h1 className="text-white text-xl font-semibold text-center">
          AI 채팅 어시스턴트
        </h1>
      </header>

      {/* JSON 데이터 표시 영역 */}
      {jsonData && (
        <div className="bg-gray-800 border-b border-gray-700 p-4">
          <h2 className="text-white text-lg font-medium mb-2">JSON 데이터:</h2>
          <pre className="bg-gray-900 text-green-400 p-3 rounded-lg overflow-x-auto text-sm">
            {JSON.stringify(jsonData, null, 2)}
          </pre>
        </div>
      )}

      {/* 메시지 영역 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center mt-20">
            <h2 className="text-white text-2xl font-medium mb-8">
              어디서부터 시작할까요?
            </h2>
            <p className="text-gray-400">
              무엇이든 물어보세요. AI가 도와드릴게요.
            </p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 text-white'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs opacity-70 mt-1">
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-700 text-white px-4 py-2 rounded-lg">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div className="bg-gray-800 border-t border-gray-700 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-4">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="무엇이든 물어보세요"
              disabled={isLoading}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
            />
            
            {/* 오른쪽 아이콘들 */}
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
              <button
                type="button"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </button>
              
              <div className="flex items-end space-x-1">
                <div className="w-1 bg-gray-400 rounded-full h-3"></div>
                <div className="w-1 bg-gray-400 rounded-full h-5"></div>
                <div className="w-1 bg-gray-400 rounded-full h-7"></div>
              </div>
            </div>
          </div>
          
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            전송
          </button>
        </form>

        {/* 하단 도구 버튼 */}
        <div className="mt-3 flex items-center">
          <button className="flex items-center text-gray-400 hover:text-white transition-colors">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span className="text-sm">도구</span>
          </button>
        </div>
      </div>
    </div>
  );
}
