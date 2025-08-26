import pickle

try:
    with open("vectordb/sr_corpus/index.pkl", "rb") as f:
        obj = pickle.load(f)
    print("✅ 로딩 성공")
except Exception as e:
    print("❌ 디버깅 실패:", e)
