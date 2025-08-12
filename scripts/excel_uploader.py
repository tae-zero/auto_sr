import pandas as pd
from sqlalchemy import create_engine
import os

class ExcelUploader:
    """엑셀 파일을 Railway PostgreSQL에 업로드하는 클래스"""
    
    def __init__(self):
        """초기화"""
        self.database_url = "postgresql://postgres:YgIQJWEaQShbuQhRsAdVaeBUZatEgrQO@gondola.proxy.rlwy.net:46735/railway"
        self.engine = None
        
        # 업로드할 파일 목록
        self.files_to_upload = [
            {
                "file_path": r"C:\taezero\auto_sr\document\직원.xlsx",
                "table_name": "employee",
                "primary_key": "id",
                "description": "직원 정보"
            },
            {
                "file_path": r"C:\taezero\auto_sr\document\손익계산.xlsx",
                "table_name": "profit_loss",
                "primary_key": "id",
                "description": "손익계산서"
            },
            {
                "file_path": r"C:\taezero\auto_sr\document\임원.xlsx",
                "table_name": "executives",
                "primary_key": "id",
                "description": "임원 정보"
            },
            {
                "file_path": r"C:\taezero\auto_sr\document\재무상태.xlsx",
                "table_name": "financial_status",
                "primary_key": "id",
                "description": "재무상태표"
            },
            {
                "file_path": r"C:\taezero\auto_sr\document\all_corp.xlsx",
                "table_name": "all_corporations",
                "primary_key": "id",
                "description": "전체 기업 정보"
            }
        ]
    
    def connect_database(self):
        """데이터베이스 연결"""
        try:
            self.engine = create_engine(self.database_url)
            # 연결 테스트
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            print("✅ Railway PostgreSQL 연결 성공!")
            return True
        except Exception as e:
            print(f"❌ 데이터베이스 연결 실패: {str(e)}")
            return False
    
    def find_file(self, file_path):
        """파일 경로 찾기 (여러 가능한 경로 시도)"""
        possible_paths = [
            file_path,
            file_path.replace("document", "documents"),
            file_path.replace("document", "data"),
            os.path.basename(file_path),  # 현재 디렉토리
            os.path.join(os.getcwd(), os.path.basename(file_path))
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                print(f"✅ 파일 발견: {path}")
                return path
        
        return None
    
    def upload_single_file(self, file_info):
        """단일 파일 업로드"""
        file_path = file_info["file_path"]
        table_name = file_info["table_name"]
        primary_key = file_info["primary_key"]
        description = file_info["description"]
        
        print(f"📁 처리 중: {os.path.basename(file_path)} → {table_name} 테이블 ({description})")
        
        # 파일 찾기
        actual_path = self.find_file(file_path)
        if not actual_path:
            print(f"   ❌ 파일을 찾을 수 없습니다: {file_path}")
            return False
        
        try:
            # 엑셀 파일 읽기
            df = pd.read_excel(actual_path)
            print(f"   📊 데이터 읽기 완료: {len(df)}행 x {len(df.columns)}열")
            print(f"   📋 컬럼명: {list(df.columns)}")
            
            # 데이터 미리보기
            print(f"   📖 데이터 미리보기:")
            print(f"      {df.head().to_string()}")
            
            # 프라이머리 키 설정
            if primary_key in df.columns:
                df = df.set_index(primary_key)
                print(f"   🔑 {primary_key} 컬럼을 프라이머리 키로 설정")
            
            # 데이터베이스에 저장
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists='replace',  # 기존 테이블이 있으면 덮어쓰기
                index=True,  # 프라이머리 키를 인덱스로 저장
                method='multi'
            )
            
            print(f"   ✅ {len(df)}행을 {table_name} 테이블에 저장 완료!")
            
            # 저장된 데이터 확인
            try:
                result = self.engine.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = result.fetchone()[0]
                print(f"   📊 데이터베이스 저장 확인: {count}행")
                
                # 컬럼 정보 확인
                result = self.engine.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)
                columns = result.fetchall()
                print(f"   📋 테이블 컬럼: {[col[0] for col in columns]}")
                
            except Exception as e:
                print(f"   ⚠️ 저장 확인 중 오류: {e}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ 처리 실패: {str(e)}")
            return False
    
    def upload_all_files(self):
        """모든 파일 업로드"""
        print("🚀 모든 엑셀 파일 업로드 시작...\n")
        
        success_count = 0
        total_count = len(self.files_to_upload)
        
        for file_info in self.files_to_upload:
            if self.upload_single_file(file_info):
                success_count += 1
            print()  # 빈 줄 추가
        
        # 최종 결과 요약
        print("📋 최종 업로드 결과:")
        try:
            with self.engine.connect() as conn:
                for file_info in self.files_to_upload:
                    table_name = file_info["table_name"]
                    description = file_info["description"]
                    try:
                        result = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = result.fetchone()[0]
                        print(f"   ✅ {table_name} ({description}): {count}행")
                    except:
                        print(f"   ❌ {table_name} ({description}): 테이블 없음")
        except Exception as e:
            print(f"   ⚠️ 결과 확인 중 오류: {e}")
        
        print(f"\n🎯 업로드 완료: {success_count}/{total_count} 파일 성공")
        print("✨ 모든 파일 업로드 완료!")
    
    def show_file_menu(self):
        """파일 선택 메뉴 표시"""
        print("\n📁 업로드할 파일 선택:")
        for i, file_info in enumerate(self.files_to_upload, 1):
            print(f"{i}. {os.path.basename(file_info['file_path'])} → {file_info['table_name']} ({file_info['description']})")
        print("6. 모든 파일 업로드")
        print("0. 종료")
    
    def run(self):
        """메인 실행 함수"""
        print("🎯 엑셀 파일 업로드 도구")
        print("=" * 50)
        
        # 데이터베이스 연결
        if not self.connect_database():
            return
        
        while True:
            self.show_file_menu()
            choice = input("\n선택하세요 (0-6): ").strip()
            
            if choice == "0":
                print("👋 프로그램을 종료합니다.")
                break
            elif choice == "6":
                self.upload_all_files()
            elif choice in ["1", "2", "3", "4", "5"]:
                idx = int(choice) - 1
                file_info = self.files_to_upload[idx]
                self.upload_single_file(file_info)
            else:
                print("❌ 잘못된 선택입니다. 다시 선택해주세요.")
            
            input("\n계속하려면 Enter를 누르세요...")

def main():
    """메인 함수"""
    uploader = ExcelUploader()
    uploader.run()

if __name__ == "__main__":
    main()
