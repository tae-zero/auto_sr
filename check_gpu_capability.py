# check_device.py (또는 1.py)
import torch

print('### PyTorch / CUDA 환경 점검 ###')

# 설치된 PyTorch 버전
print('토치 버전:', torch.__version__)

# CUDA 가능 여부
USE_CUDA = torch.cuda.is_available()
print('CUDA 사용 가능 여부:', USE_CUDA)

# 학습 디바이스 선택
device = torch.device('cuda:0' if USE_CUDA else 'cpu')
print('학습을 진행하는 기기:', device)

# GPU 정보 (CUDA가 있을 때만)
if USE_CUDA:
    try:
        gpu_count = torch.cuda.device_count()
        print('사용 가능 GPU 갯수:', gpu_count)
        for idx in range(gpu_count):
            print(f'GPU {idx} 이름:', torch.cuda.get_device_name(idx))
        # 선택된 디바이스의 이름(보통 0번)
        print('선택된 GPU:', torch.cuda.get_device_name(0))
    except Exception as e:
        print('GPU 정보 조회 중 오류:', e)
else:
    print('GPU가 없어 CPU로 실행합니다.')

# 선택 요약 한 줄
print('요약:', f"{'GPU 사용' if USE_CUDA else 'CPU 사용'} / device={device}")
