import { NextRequest, NextResponse } from 'next/server';

// Frontend는 단순히 Gateway로 요청을 전달하는 프록시 역할만 수행
const GATEWAY_URL = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8080';

// GET: 재무정보 조회 - Gateway를 통해 TCFD Service 호출
export async function GET(request: NextRequest) {
  try {
    // Gateway를 통해 TCFD Service의 재무정보 조회
    const response = await fetch(`${GATEWAY_URL}/api/v1/financial-data`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // JWT 토큰이 있다면 추가
        ...(request.headers.get('authorization') && {
          'Authorization': request.headers.get('authorization')!
        })
      },
    });

    if (!response.ok) {
      throw new Error(`재무정보 조회 실패: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('재무정보 조회 오류:', error);
    return NextResponse.json(
      { error: '재무정보를 불러오는데 실패했습니다.' },
      { status: 500 }
    );
  }
}

// POST: 재무정보 저장 - Gateway를 통해 TCFD Service 호출
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Gateway를 통해 TCFD Service의 재무정보 저장
    const response = await fetch(`${GATEWAY_URL}/api/v1/financial-data`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // JWT 토큰이 있다면 추가
        ...(request.headers.get('authorization') && {
          'Authorization': request.headers.get('authorization')!
        })
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`재무정보 저장 실패: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('재무정보 저장 오류:', error);
    return NextResponse.json(
      { error: '재무정보 저장에 실패했습니다.' },
      { status: 500 }
    );
  }
}

// PUT: 재무정보 업데이트 - Gateway를 통해 TCFD Service 호출
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Gateway를 통해 TCFD Service의 재무정보 업데이트
    const response = await fetch(`${GATEWAY_URL}/api/v1/financial-data`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        // JWT 토큰이 있다면 추가
        ...(request.headers.get('authorization') && {
          'Authorization': request.headers.get('authorization')!
        })
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      throw new Error(`재무정보 업데이트 실패: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('재무정보 업데이트 오류:', error);
    return NextResponse.json(
      { error: '재무정보 업데이트에 실패했습니다.' },
      { status: 500 }
    );
  }
}

// DELETE: 재무정보 삭제 - Gateway를 통해 TCFD Service 호출
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const companyId = searchParams.get('company_id');
    const fiscalYear = searchParams.get('fiscal_year');

    if (!companyId || !fiscalYear) {
      return NextResponse.json(
        { error: '회사 ID와 회계연도가 필요합니다.' },
        { status: 400 }
      );
    }

    // Gateway를 통해 TCFD Service의 재무정보 삭제
    const response = await fetch(`${GATEWAY_URL}/api/v1/financial-data?company_id=${companyId}&fiscal_year=${fiscalYear}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        // JWT 토큰이 있다면 추가
        ...(request.headers.get('authorization') && {
          'Authorization': request.headers.get('authorization')!
        })
      },
    });

    if (!response.ok) {
      throw new Error(`재무정보 삭제 실패: ${response.status}`);
    }

    return NextResponse.json({ message: '재무정보가 성공적으로 삭제되었습니다.' });
  } catch (error) {
    console.error('재무정보 삭제 오류:', error);
    return NextResponse.json(
      { error: '재무정보 삭제에 실패했습니다.' },
      { status: 500 }
    );
  }
}
