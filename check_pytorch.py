
import torch, sympy, importlib
print("torch:", torch.__version__, "CUDA:", torch.version.cuda)
import torchvision, torchaudio
print("torchvision:", torchvision.__version__)
print("torchaudio:", torchaudio.__version__)
print("sympy:", sympy.__version__)
print("pydantic-settings:", importlib.import_module("pydantic_settings").__version__)

