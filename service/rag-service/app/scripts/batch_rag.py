# app/scripts/batch_rag.py
import os
import sys
import time
import pandas as pd

# 레포 루트에서 실행 가정:  python -m app.scripts.batch_rag --csv "C:\...\rag_questions.csv"
# 필요한 경우 아래 두 줄로 워킹디렉토리 조정
# os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app.query import QueryReq, query  # 내부 함수 직접 호출 → /rag/query와 동일 로직 + JSONL 로깅 동작

def main(csv_path: str, top_k: int = 5, collections=None, out_log_path: str = None, sleep_sec: float = 0.0):
    if collections is None:
        collections = ["sr_corpus", "standards"]

    # 배치 실행 결과를 별도 로그 파일로 분리하고 싶다면 환경변수로 임시 지정
    if out_log_path:
        os.makedirs(os.path.dirname(out_log_path), exist_ok=True)
        os.environ["QA_JSONL_PATH"] = out_log_path

    df = pd.read_csv(csv_path, encoding="utf-8")
    if "question" not in df.columns:
        raise ValueError("CSV에 'question' 컬럼이 필요합니다.")

    total = 0
    ok = 0
    for q in df["question"].astype(str).fillna("").map(str.strip):
        total += 1
        if not q:
            continue
        try:
            req = QueryReq(question=q, top_k=top_k, collections=collections)
            res = query(req)   # ← FastAPI 엔드포인트와 동일 로직 수행 + JSONL 로깅 자동 수행
            ok += 1
        except Exception as e:
            print(f"[WARN] 실패: {q[:60]}... -> {e}")
        if sleep_sec > 0:
            time.sleep(sleep_sec)

    print(f"[DONE] total={total}, success={ok}, log={os.getenv('QA_JSONL_PATH')}")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--csv", required=True, help="질문 CSV 파일 경로 (question 컬럼 필수)")
    p.add_argument("--top_k", type=int, default=5)
    p.add_argument("--collections", nargs="*", default=["sr_corpus", "standards"])
    p.add_argument("--out_log", default="", help="결과 Q&A를 쌓을 JSONL 경로(미지정 시 .env의 QA_JSONL_PATH 사용)")
    p.add_argument("--sleep", type=float, default=0.0, help="요청 간 대기(초) - GPU/메모리 보호용")
    args = p.parse_args()

    out_log = args.out_log if args.out_log.strip() else None
    main(csv_path=args.csv, top_k=args.top_k, collections=args.collections, out_log_path=out_log, sleep_sec=args.sleep)
