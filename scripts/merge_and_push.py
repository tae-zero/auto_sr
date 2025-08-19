# -*- coding: utf-8 -*-
"""
LoRA 병합 & Hugging Face 업로드 도구

사용 예시 (PowerShell):
# 1) 어댑터만 업로드
python merge_and_push.py `
  --base_model beomi/KoAlpaca-Polyglot-5.8B `
  --lora_path C:\taezero\auto_sr\service\tcfdreport-service\outputs\koalpaca-5p8b-lora `
  --out_dir C:\taezero\auto_sr\service\tcfdreport-service\outputs\merged `
  --repo_id_adapter your-org/koalpaca-5p8b-tcfd-lora `
  --push adapter --private

# 2) 병합본 업로드
python merge_and_push.py `
  --base_model beomi/KoAlpaca-Polyglot-5.8B `
  --lora_path C:\...\outputs\koalpaca-5p8b-lora `
  --out_dir C:\...\outputs\merged `
  --repo_id_merged your-org/koalpaca-5p8b-tcfd-merged `
  --push merged --private

# 3) 둘 다 업로드
python merge_and_push.py --push both ...
"""

import os
import argparse
import shutil
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from huggingface_hub import HfApi, create_repo, upload_folder

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--base_model", type=str, required=True,
                   help="예: beomi/KoAlpaca-Polyglot-5.8B 또는 kakaobrain/polyglot-ko-3.8b")
    p.add_argument("--lora_path", type=str, required=True,
                   help="train_sft_vram_aware.py 결과(LoRA 어댑터) 폴더")
    p.add_argument("--out_dir", type=str, required=True,
                   help="병합 결과 저장 폴더(임시 포함)")
    p.add_argument("--push", type=str, default="adapter", choices=["adapter","merged","both"])
    p.add_argument("--repo_id_adapter", type=str, default=None,
                   help="어댑터 업로드 HF Repo ID (예: your-org/model-lora)")
    p.add_argument("--repo_id_merged", type=str, default=None,
                   help="병합 업로드 HF Repo ID (예: your-org/model-merged)")
    p.add_argument("--private", action="store_true", default=False,
                   help="HF repo private로 생성")
    p.add_argument("--trust_remote_code", action="store_true", default=True)
    return p.parse_args()

def ensure_dir(p: str | Path):
    Path(p).mkdir(parents=True, exist_ok=True)

def save_adapter_copy(lora_path: str, adapter_out: str):
    # 어댑터 폴더 그대로 복사 (tokenizer는 base에서 별도로 저장 권장)
    if os.path.exists(adapter_out):
        shutil.rmtree(adapter_out)
    shutil.copytree(lora_path, adapter_out)

def merge_lora(base_model: str, lora_path: str, merged_out: str, trust_remote_code=True):
    """
    LoRA → base에 병합 (PEFT merge_and_unload) 후 safetensors로 저장
    """
    print("[Merge] Loading base model:", base_model)
    tok = AutoTokenizer.from_pretrained(base_model, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    base = AutoModelForCausalLM.from_pretrained(
        base_model,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=trust_remote_code,
    )
    print("[Merge] Attaching LoRA from:", lora_path)
    model = PeftModel.from_pretrained(base, lora_path, is_trainable=False)
    print("[Merge] Merging LoRA into base...")
    merged = model.merge_and_unload()

    ensure_dir(merged_out)
    print("[Merge] Saving merged model to:", merged_out)
    merged.save_pretrained(merged_out, safe_serialization=True)
    tok.save_pretrained(merged_out)

def hf_upload(local_dir: str, repo_id: str, private: bool):
    """
    HF 업로드. 사전 준비:
    - 환경변수 HF_TOKEN 설정 또는 huggingface-cli login
    """
    api = HfApi()
    print(f"[HF] Creating repo: {repo_id} (private={private})")
    create_repo(repo_id=repo_id, private=private, exist_ok=True)
    print(f"[HF] Uploading from {local_dir} ...")
    upload_folder(repo_id=repo_id, folder_path=local_dir, commit_message="upload model")

def main():
    args = parse_args()
    ensure_dir(args.out_dir)

    adapter_out = os.path.join(args.out_dir, "adapter_export")
    merged_out  = os.path.join(args.out_dir, "merged_export")

    # (A) 어댑터 업로드
    if args.push in ("adapter", "both"):
        if not args.repo_id_adapter:
            raise ValueError("--repo_id_adapter 를 지정하세요 (예: your-org/model-lora)")
        print("[Adapter] Preparing adapter folder...")
        save_adapter_copy(args.lora_path, adapter_out)

        # 토크나이저도 함께 올리고 싶으면 base에서 복사
        try:
            tok_tmp = os.path.join(args.out_dir, "_tokenizer_tmp")
            ensure_dir(tok_tmp)
            tok = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
            tok.save_pretrained(tok_tmp)
            # tokenizer.json/tokenizer_config.json 등 필요한 파일을 어댑터 폴더에 복사
            for f in os.listdir(tok_tmp):
                src = os.path.join(tok_tmp, f)
                dst = os.path.join(adapter_out, f)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
            shutil.rmtree(tok_tmp)
        except Exception as e:
            print("[Adapter] tokenizer copy skipped:", e)

        print("[Adapter] Uploading to HF:", args.repo_id_adapter)
        hf_upload(adapter_out, args.repo_id_adapter, args.private)

    # (B) 병합 업로드
    if args.push in ("merged", "both"):
        if not args.repo_id_merged:
            raise ValueError("--repo_id_merged 를 지정하세요 (예: your-org/model-merged)")
        print("[Merged] Building merged weights...")
        merge_lora(args.base_model, args.lora_path, merged_out, args.trust_remote_code)
        print("[Merged] Uploading to HF:", args.repo_id_merged)
        hf_upload(merged_out, args.repo_id_merged, args.private)

    print(">>> Done.")

if __name__ == "__main__":
    # HF_TOKEN 이 환경변수에 있어야 업로드가 원활합니다.
    # setx HF_TOKEN "hf_xxx"  (PowerShell)
    main()
