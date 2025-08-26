with open(r'C:\taezero\auto_sr\service\llm-service\vectordb\sr_corpus\index.pkl', 'rb') as f:
    content = f.read()

print(b"pydantic" in content)   # 'pydantic' 문자열이 존재하는지
print(b"pydantic_core" in content)  # core가 따로 직렬화됐는지

for line in content.split(b'\n'):
    if b'pydantic' in line:
        print(line)