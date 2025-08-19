# -*- coding: utf-8 -*-
"""
==============================================================
VRAM 가이드 (대략적인 감, 4-bit QLoRA 기준, LoRA r=16, seq ≤ 1k)
--------------------------------------------------------------
모델                         파라미터     추론 VRAM      학습 VRAM
Polyglot‑Ko 1.3B             1.3B        ~1.5–2 GB     ~2–3 GB
Polyglot‑Ko 3.8B             3.8B        ~2.5–3.5 GB   ~3–5 GB
KoAlpaca/Polyglot 5.8B       5.8B        ~3–4.5 GB     ~5–7.5 GB
--------------------------------------------------------------
※ 정확치는 시퀀스 길이, LoRA r, gradient_accumulation_steps 등에 따라 달라집니다.
※ RTX 2080(8GB)에서는 5.8B도 QLoRA + grad_accum으로 가능하지만 여유는 적습니다.
==============================================================

데이터(JSONL) 형식 예:
{"instruction":"...", "input":"근거 텍스트...", "output":"모델이 써야 할 정답 문단...", "metadata":{...}}
"""

import os
import json
import argparse
from typing import Dict, Tuple

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
)
from trl import SFTTrainer, DataCollatorForCompletionOnlyLM

MODEL_ID_BY_SIZE = {
    "1.3b": "kakaobrain/polyglot-ko-1.3b",
    "3.8b": "kakaobrain/polyglot-ko-3.8b",
    "5.8b": "beomi/KoAlpaca-Polyglot-5.8B",
}

def recommended_hparams(model_size: str) -> Dict:
    if model_size == "1.3b":
        return dict(max_seq_len=1024, lora_r=16, grad_accum=16, batch_size=1, lr=2e-4)
    if model_size == "3.8b":
        return dict(max_seq_len=1024, lora_r=16, grad_accum=24, batch_size=1, lr=2e-4)
    return dict(max_seq_len=1024, lora_r=16, grad_accum=32, batch_size=1, lr=2e-4)  # 5.8b

def get_vram_info() -> Tuple[bool, float, str]:
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        return True, props.total_memory / (1024**3), props.name
    return False, 0.0, "CPU"

def format_example(ex: Dict, tok) -> Dict:
    inst = (ex.get("instruction") or "").strip()
    inp  = (ex.get("input") or "").strip()
    out  = (ex.get("output") or "").strip()
    prompt = f"[INST] {inst}\n\n[근거]\n{inp}\n[/INST]\n"
    return {"text": prompt + out + tok.eos_token}

def build_bnb_config(fp16=True) -> BitsAndBytesConfig:
    compute_dtype = torch.float16 if fp16 else torch.bfloat16
    return BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
        bnb_4bit_quant_type="nf4",
    )

def neox_lora_config(r=16, alpha=32, dropout=0.1) -> LoraConfig:
    target_modules = ["query_key_value", "dense", "dense_h_to_4h", "dense_4h_to_h"]
    return LoraConfig(
        r=r, lora_alpha=alpha, lora_dropout=dropout,
        bias="none", task_type="CAUSAL_LM", target_modules=target_modules
    )

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--data_path", type=str,
                   default=r"C:\taezero\auto_sr\document\qa_candidates.jsonl")
    p.add_argument("--out_dir", type=str,
                   default=r"C:\taezero\auto_sr\service\tcfdreport-service\outputs\lora")
    p.add_argument("--model_size", type=str, default="5.8b",
                   choices=["1.3b", "3.8b", "5.8b"])
    p.add_argument("--base_model", type=str, default=None)
    p.add_argument("--max_seq_len", type=int, default=None)
    p.add_argument("--lora_r", type=int, default=None)
    p.add_argument("--grad_accum", type=int, default=None)
    p.add_argument("--batch_size", type=int, default=None)
    p.add_argument("--lr", type=float, default=None)
    p.add_argument("--epochs", type=int, default=1)
    p.add_argument("--fp16", action="store_true", default=True)
    p.add_argument("--bf16", action="store_true", default=False)
    p.add_argument("--warmup_ratio", type=float, default=0.03)
    p.add_argument("--logging_steps", type=int, default=10)
    p.add_argument("--save_steps", type=int, default=1000)
    p.add_argument("--save_total_limit", type=int, default=2)
    p.add_argument("--packing", action="store_true", default=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--trust_remote_code", action="store_true", default=True)
    return p.parse_args()

def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    torch.manual_seed(args.seed)

    model_id = args.base_model or MODEL_ID_BY_SIZE[args.model_size]
    rec = recommended_hparams(args.model_size)
    max_seq_len = args.max_seq_len or rec["max_seq_len"]
    lora_r      = args.lora_r      or rec["lora_r"]
    grad_accum  = args.grad_accum  or rec["grad_accum"]
    batch_size  = args.batch_size  or rec["batch_size"]
    lr          = args.lr          or rec["lr"]

    has_cuda, vram_gb, dev_name = get_vram_info()
    print(f"[GPU] available={has_cuda}, device='{dev_name}', total_vram≈{vram_gb:.1f} GB")
    print(f"[MODEL] id={model_id}, size={args.model_size}")
    print(f"[HYPER] seq_len={max_seq_len}, lora_r={lora_r}, grad_accum={grad_accum}, batch={batch_size}, lr={lr}")

    qcfg = build_bnb_config(fp16=args.fp16)

    tok = AutoTokenizer.from_pretrained(model_id, use_fast=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id, device_map="auto", quantization_config=qcfg,
        trust_remote_code=args.trust_remote_code
    )

    if getattr(model, "is_loaded_in_4bit", False):
        model = prepare_model_for_kbit_training(model)

    lora_cfg = neox_lora_config(r=lora_r, alpha=32, dropout=0.1)
    model = get_peft_model(model, lora_cfg)

    ds = load_dataset("json", data_files=args.data_path, split="train")
    ds = ds.map(lambda ex: format_example(ex, tok), remove_columns=ds.column_names)
    collator = DataCollatorForCompletionOnlyLM(response_template=None, tokenizer=tok)

    targs = TrainingArguments(
        output_dir=args.out_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=grad_accum,
        learning_rate=lr,
        lr_scheduler_type="cosine",
        warmup_ratio=args.warmup_ratio,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        save_total_limit=args.save_total_limit,
        fp16=bool(args.fp16),
        bf16=bool(args.bf16),
        gradient_checkpointing=True,
        optim="paged_adamw_8bit",
        max_grad_norm=0.3,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model, tokenizer=tok, train_dataset=ds,
        data_collator=collator, packing=bool(args.packing),
        max_seq_length=max_seq_len, args=targs,
    )

    print(">>> Training start")
    try:
        trainer.train()
    except RuntimeError as e:
        if "CUDA out of memory" in str(e):
            print("\n[OOM] 조정 팁:")
            print("- --max_seq_len 768 또는 640")
            print("- --lora_r 8")
            print("- --grad_accum 32~48")
        raise

    print(">>> Saving LoRA adapters to", args.out_dir)
    trainer.save_model(args.out_dir)

    with open(os.path.join(args.out_dir, "lora_cfg.json"), "w", encoding="utf-8") as f:
        json.dump(
            {"model_id": model_id, "size": args.model_size, "r": lora_r,
             "alpha": 32, "dropout": 0.1, "max_seq_len": max_seq_len,
             "grad_accum": grad_accum, "batch_size": batch_size, "lr": lr},
            f, ensure_ascii=False, indent=2
        )

if __name__ == "__main__":
    os.environ.setdefault("BITSANDBYTES_NOWELCOME", "1")
    os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "max_split_size_mb:128")
    main()
