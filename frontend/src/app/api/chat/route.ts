import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json();

    if (!message) {
      return NextResponse.json(
        { error: '메시지가 필요합니다.' },
        { status: 400 }
      );
    }

    // 여기서 실제 AI 서비스와 연동할 수 있습니다
    // 현재는 간단한 응답을 반환합니다
    const response = {
      message: `안녕하세요! "${message}"에 대한 답변입니다. 현재는 데모 모드로 작동하고 있습니다.`,
      timestamp: new Date().toISOString(),
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('채팅 API 오류:', error);
    return NextResponse.json(
      { error: '서버 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // 채팅 히스토리를 반환하는 로직
    const history = [
      {
        id: '1',
        content: '안녕하세요! 무엇을 도와드릴까요?',
        role: 'assistant',
        timestamp: new Date().toISOString(),
      },
    ];

    return NextResponse.json(history);
  } catch (error) {
    console.error('채팅 히스토리 API 오류:', error);
    return NextResponse.json(
      { error: '서버 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
}

export async function DELETE() {
  try {
    // 채팅 히스토리 삭제 로직
    return NextResponse.json({ message: '채팅 히스토리가 삭제되었습니다.' });
  } catch (error) {
    console.error('채팅 히스토리 삭제 API 오류:', error);
    return NextResponse.json(
      { error: '서버 오류가 발생했습니다.' },
      { status: 500 }
    );
  }
} 