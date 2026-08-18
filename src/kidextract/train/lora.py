from __future__ import annotations

import json
import time
from pathlib import Path

import torch
from peft import LoraConfig as PeftLoraConfig
from transformers import AutoTokenizer
from trl import SFTConfig, SFTTrainer

from .config import ExperimentConfig
from .data import load_split


def build_peft_config(config: ExperimentConfig) -> PeftLoraConfig:
    return PeftLoraConfig(
        r=config.lora.r,
        lora_alpha=config.lora.alpha,
        lora_dropout=config.lora.dropout,
        target_modules=list(config.lora.target_modules),
        bias="none",
        task_type="CAUSAL_LM",
    )


def build_sft_config(config: ExperimentConfig) -> SFTConfig:
    return SFTConfig(
        output_dir=str(config.output.dir),
        max_length=config.model.max_seq_length,
        completion_only_loss=True,
        packing=False,
        num_train_epochs=config.training.epochs,
        learning_rate=config.training.learning_rate,
        per_device_train_batch_size=config.training.batch_size,
        per_device_eval_batch_size=config.training.batch_size,
        gradient_accumulation_steps=config.training.gradient_accumulation_steps,
        warmup_steps=config.training.warmup_steps,
        weight_decay=config.training.weight_decay,
        lr_scheduler_type=config.training.lr_scheduler,
        logging_steps=config.training.logging_steps,
        eval_strategy="steps",
        eval_steps=config.training.eval_steps,
        save_strategy="no",
        seed=config.training.seed,
        use_cpu=not torch.cuda.is_available(),
        bf16=False,
        fp16=False,
        dataloader_num_workers=0,
        report_to=[],
        disable_tqdm=False,
    )


def run(config: ExperimentConfig, threads: int | None = None) -> dict:
    if threads:
        torch.set_num_threads(threads)

    train_dataset = load_split(config.data.dir / config.data.train_file, config.data.max_train_samples)
    eval_dataset = load_split(config.data.dir / config.data.validation_file, config.data.max_eval_samples)

    tokenizer = AutoTokenizer.from_pretrained(config.model.name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    trainer = SFTTrainer(
        model=config.model.name,
        args=build_sft_config(config),
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        processing_class=tokenizer,
        peft_config=build_peft_config(config),
    )

    started = time.time()
    result = trainer.train()
    duration = time.time() - started

    output_dir = Path(config.output.dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(output_dir / "adapter"))
    tokenizer.save_pretrained(str(output_dir / "adapter"))

    trainable = sum(p.numel() for p in trainer.model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in trainer.model.parameters())
    summary = {
        "config": config.to_dict(),
        "train_runtime_seconds": round(duration, 1),
        "train_loss": result.training_loss,
        "steps": result.global_step,
        "trainable_parameters": trainable,
        "total_parameters": total,
        "trainable_fraction": round(trainable / total, 6),
        "train_examples": len(train_dataset),
        "eval_examples": len(eval_dataset),
    }
    metrics = trainer.evaluate()
    summary["eval_loss"] = metrics.get("eval_loss")
    (output_dir / "training_summary.json").write_text(json.dumps(summary, indent=2))
    return summary
