# AI 채팅 어시스턴트

Next.js, TypeScript, React, Zustand, Axios를 사용한 PWA 채팅 애플리케이션입니다.

## 🚀 기술 스택

- **Frontend**: Next.js 14, React 18, TypeScript
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS
- **PWA**: next-pwa
- **Deployment**: Vercel
- **CI/CD**: GitHub Actions

## 📋 기능

- 🤖 AI 채팅 인터페이스
- 📱 PWA (Progressive Web App) 지원
- 🎨 다크 테마 UI
- 📝 실시간 메시지 전송
- 💾 채팅 히스토리 관리
- 🔄 자동 스크롤
- ⚡ 로딩 상태 표시

## 🛠️ 설치 및 실행

### 1. 저장소 클론
```bash
git clone <your-repository-url>
cd my-app
```

### 2. 의존성 설치
```bash
npm install
```

### 3. 환경 변수 설정
```bash
cp env.example .env.local
```
`.env.local` 파일을 편집하여 필요한 환경 변수를 설정하세요.

### 4. 개발 서버 실행
```bash
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 열어 애플리케이션을 확인하세요.

## 🏗️ 빌드 및 배포

### 프로덕션 빌드
```bash
npm run build
```

### 프로덕션 서버 실행
```bash
npm start
```

## 📱 PWA 기능

이 애플리케이션은 PWA로 구성되어 있어 다음과 같은 기능을 제공합니다:

- 📱 홈 화면에 추가 가능
- 🔄 오프라인 지원 (향후 구현 예정)
- 📲 네이티브 앱과 유사한 경험

## 🔄 CI/CD 파이프라인

GitHub Actions를 통해 자동화된 CI/CD 파이프라인이 구성되어 있습니다:

1. **Lint & Type Check**: ESLint와 TypeScript 타입 체크
2. **Test**: 테스트 실행 (추후 추가 예정)
3. **Build**: 프로덕션 빌드
4. **Deploy**: Vercel 자동 배포 (main 브랜치)

### GitHub Secrets 설정

Vercel 배포를 위해 다음 GitHub Secrets를 설정해야 합니다:

- `VERCEL_TOKEN`: Vercel API 토큰
- `VERCEL_ORG_ID`: Vercel 조직 ID
- `VERCEL_PROJECT_ID`: Vercel 프로젝트 ID

## 📁 프로젝트 구조

```
my-app/
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── api/            # API 라우트
│   │   ├── globals.css     # 전역 스타일
│   │   ├── layout.tsx      # 루트 레이아웃
│   │   └── page.tsx        # 메인 페이지
│   ├── services/           # API 서비스
│   │   ├── api.ts          # Axios 설정
│   │   └── chatService.ts  # 채팅 API 서비스
│   └── store/              # Zustand 스토어
│       └── chatStore.ts    # 채팅 상태 관리
├── public/                 # 정적 파일
│   └── manifest.json       # PWA 매니페스트
├── .github/workflows/      # GitHub Actions
└── package.json
```

## 🎨 커스터마이징

### 테마 변경
`src/app/globals.css`에서 CSS 변수를 수정하여 테마를 변경할 수 있습니다.

### API 엔드포인트 변경
`src/services/api.ts`에서 `baseURL`을 수정하여 API 엔드포인트를 변경할 수 있습니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해 주세요.
