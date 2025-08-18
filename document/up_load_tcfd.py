import os
import pandas as pd
from sqlalchemy import create_engine, text

class SingleExcelUploader:
    """tcfd_standard.xlsx 단일 파일을 Railway PostgreSQL에 업로드 (컬럼 원본 그대로)"""
    def __init__(self):
        # 외부 접속 가능한 Railway 프록시 연결 문자열 (필요시 내부 DNS로 교체)
        self.connection_string = (
            "postgresql://postgres:YgIQJWEaQShbuQhRsAdVaeBUZatEgrQO@"
            "gondola.proxy.rlwy.net:46735/railway"
        )
        self.engine = None

        # 업로드 대상 단일 파일과 테이블명 (파일명=테이블명)
        self.file_path = r"C:\taezero\auto_sr\document\tcfd_standard.xlsx"
        self.table_name = "tcfd_standard"  # os.path.splitext(os.path.basename(self.file_path))[0] 와 동일

    def connect_database(self) -> bool:
        try:
            self.engine = create_engine(self.connection_string, echo=False, pool_pre_ping=True)
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Railway PostgreSQL 연결 성공")
            return True
        except Exception as e:
            print(f"❌ DB 연결 실패: {e}")
            return False

    def upload(self) -> bool:
        if not os.path.exists(self.file_path):
            print(f"❌ 파일을 찾을 수 없습니다: {self.file_path}")
            return False

        try:
            # 1) 엑셀 로드 (첫 시트)
            df = pd.read_excel(self.file_path)
            print(f"📊 원본 데이터: {len(df)}행 x {len(df.columns)}열")
            print(f"🧾 컬럼: {list(df.columns)}")

            # 2) 컬럼/데이터 가공 없이 그대로 저장 (index=False)
            df.to_sql(
                name=self.table_name,
                con=self.engine,
                if_exists="replace",  # 기존 테이블 있으면 교체
                index=False,          # 인덱스 컬럼 생성 X (원본 그대로)
                method="multi",
            )
            print(f"✅ {len(df)}행을 '{self.table_name}' 테이블에 저장 완료")

            # 3) 저장 검증
            with self.engine.connect() as conn:
                count = conn.execute(text(f'SELECT COUNT(*) FROM "{self.table_name}"')).scalar()
                cols = conn.execute(text(f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = :t
                    ORDER BY ordinal_position
                """), {"t": self.table_name}).fetchall()
                print(f"📌 DB 저장 확인: {count}행")
                print(f"📋 DB 컬럼: {[c[0] for c in cols]}")
            return True

        except Exception as e:
            print(f"❌ 업로드 실패: {e}")
            return False


def main():
    uploader = SingleExcelUploader()
    if uploader.connect_database():
        uploader.upload()

if __name__ == "__main__":
    main()
