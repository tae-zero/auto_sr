import pdfplumber

pdf_path = "현대모비스_지속가능성보고서2022.pdf"

tcfd_text = ""

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        if text and "TCFD 지지 선언" in text:
            # "TCFD 지지 선언" 포함된 부분부터 끝까지 추출
            lines = text.splitlines()
            capture = False
            extracted = []
            for line in lines:
                if "TCFD 지지 선언" in line:
                    capture = True
                if capture:
                    extracted.append(line)
            tcfd_text = "\n".join(extracted)
            break  # 첫 번째 발견된 페이지만 추출

print(tcfd_text)