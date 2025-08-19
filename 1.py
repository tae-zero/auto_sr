import faiss

print("faiss version:", faiss.__version__)
print("faiss available GPU:", faiss.get_num_gpus())