import pandas as pd
from sqlalchemy import create_engine, text
import os
import sys

class CorporationOverviewUploader:
    """기업개요 CSV 파일을 Railway PostgreSQL에 업로드하는 클래스"""
    
    def __init__(self):
        """초기화"""
        # Railway PostgreSQL 연결 문자열 (실제 값으로 교체 필요)
        self.database_url = "postgresql://postgres:YgIQJWEaQShbuQhRsAdVaeBUZatEgrQO@gondola.proxy.rlwy.net:46735/railway"
        self.engine = None
        
        # 업로드할 파일 정보
        self.file_info = {
            "file_path": r"dart/기업개요.csv",
            "table_name": "corporation_overview",
            "primary_key": "종목코드",
            "description": "기업개요 정보"
        }
    
    def connect_database(self):
        """데이터베이스 연결"""
        try:
            print("🔌 데이터베이스 연결 시도 중...")
            
            # 환경변수에서 데이터베이스 URL 가져오기
            db_url = os.getenv('DATABASE_URL')
            if db_url:
                # Railway 환경변수 형식을 SQLAlchemy 형식으로 변환
                if db_url.startswith('postgres://'):
                    db_url = db_url.replace('postgres://', 'postgresql://', 1)
                self.database_url = db_url
                print("✅ 환경변수에서 데이터베이스 URL을 가져왔습니다.")
            else:
                print("⚠️ 환경변수 DATABASE_URL이 설정되지 않았습니다.")
                print("📝 .env 파일에 DATABASE_URL을 설정하거나 직접 입력해주세요.")
                self.database_url = input("데이터베이스 URL을 입력하세요: ").strip()
            
            if not self.database_url:
                raise ValueError("데이터베이스 URL이 입력되지 않았습니다.")
            
            # 데이터베이스 연결
            self.engine = create_engine(self.database_url)
            
            # 연결 테스트
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✅ 데이터베이스 연결 성공!")
                
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {e}")
            sys.exit(1)
    
    def find_file(self, file_path):
        """파일 존재 여부 확인"""
        if os.path.exists(file_path):
            print(f"✅ 파일 발견: {file_path}")
            return True
        else:
            print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
            return False
    
    def create_table(self):
        """기업개요 테이블 생성"""
        try:
            print("🏗️ 기업개요 테이블 생성 중...")
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS corporation_overview (
                id SERIAL PRIMARY KEY,
                종목코드 VARCHAR(20) UNIQUE NOT NULL,
                종목명 VARCHAR(200) NOT NULL,
                주소 TEXT,
                설립일 DATE,
                대표자 VARCHAR(200),
                전화번호 VARCHAR(50),
                홈페이지 TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            -- 인덱스 생성
            CREATE INDEX IF NOT EXISTS idx_corporation_overview_종목코드 ON corporation_overview(종목코드);
            CREATE INDEX IF NOT EXISTS idx_corporation_overview_종목명 ON corporation_overview(종목명);
            """
            
            with self.engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
            
            print("✅ 기업개요 테이블 생성 완료!")
            
        except Exception as e:
            print(f"❌ 테이블 생성 실패: {e}")
            raise
    
    def upload_data(self):
        """CSV 데이터 업로드"""
        try:
            print("📤 데이터 업로드 시작...")
            
            # CSV 파일 읽기
            df = pd.read_csv(self.file_info["file_path"], encoding='utf-8')
            print(f"📊 CSV 파일 읽기 완료: {len(df)}개 행")
            
            # 컬럼명 확인 및 출력
            print("📋 컬럼명:")
            for i, col in enumerate(df.columns):
                print(f"  {i+1}. {col}")
            
            # 데이터 전처리
            print("🔧 데이터 전처리 중...")
            
            # 설립일 컬럼을 DATE 타입으로 변환
            df['설립일'] = pd.to_datetime(df['설립일'], errors='coerce')
            
            # 빈 문자열을 None으로 변환
            df = df.replace('', None)
            
            # 데이터베이스에 업로드
            print("💾 데이터베이스에 업로드 중...")
            
            # 기존 데이터 삭제 (선택사항)
            with self.engine.connect() as conn:
                # 기존 데이터 확인
                result = conn.execute(text("SELECT COUNT(*) FROM corporation_overview"))
                existing_count = result.scalar()
                print(f"📊 기존 데이터 수: {existing_count}개")
                
                if existing_count > 0:
                    delete_choice = input("기존 데이터를 모두 삭제하고 새로 업로드하시겠습니까? (y/N): ").strip().lower()
                    if delete_choice == 'y':
                        conn.execute(text("DELETE FROM corporation_overview"))
                        conn.commit()
                        print("🗑️ 기존 데이터 삭제 완료")
                    else:
                        print("📝 기존 데이터를 유지하고 새 데이터만 추가합니다.")
            
            # 데이터 업로드
            df.to_sql(
                'corporation_overview', 
                self.engine, 
                if_exists='append', 
                index=False,
                method='multi',
                chunksize=1000
            )
            
            print("✅ 데이터 업로드 완료!")
            
            # 업로드 결과 확인
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM corporation_overview"))
                total_count = result.scalar()
                print(f"📊 총 데이터 수: {total_count}개")
                
                # 샘플 데이터 확인
                result = conn.execute(text("SELECT * FROM corporation_overview LIMIT 5"))
                sample_data = result.fetchall()
                print("\n📋 샘플 데이터:")
                for row in sample_data:
                    print(f"  - {row[1]} ({row[2]})")
            
        except Exception as e:
            print(f"❌ 데이터 업로드 실패: {e}")
            raise
    
    def show_file_menu(self):
        """파일 메뉴 표시"""
        print("\n" + "="*50)
        print("🏢 기업개요 데이터 업로더")
        print("="*50)
        print(f"📁 파일 경로: {self.file_info['file_path']}")
        print(f"🗃️ 테이블명: {self.file_info['table_name']}")
        print(f"🔑 기본키: {self.file_info['primary_key']}")
        print(f"📝 설명: {self.file_info['description']}")
        print("="*50)
    
    def run(self):
        """메인 실행 함수"""
        try:
            print("🚀 기업개요 데이터 업로더 시작")
            
            # 파일 존재 확인
            if not self.find_file(self.file_info["file_path"]):
                return
            
            # 메뉴 표시
            self.show_file_menu()
            
            # 사용자 확인
            confirm = input("\n계속 진행하시겠습니까? (y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ 업로드가 취소되었습니다.")
                return
            
            # 데이터베이스 연결
            self.connect_database()
            
            # 테이블 생성
            self.create_table()
            
            # 데이터 업로드
            self.upload_data()
            
            print("\n🎉 모든 작업이 완료되었습니다!")
            
        except Exception as e:
            print(f"\n❌ 오류 발생: {e}")
            sys.exit(1)
        finally:
            if self.engine:
                self.engine.dispose()
                print("🔌 데이터베이스 연결 종료")

def main():
    """메인 함수"""
    uploader = CorporationOverviewUploader()
    uploader.run()

if __name__ == "__main__":
    main()
