from __future__ import annotations

from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList

from .runner import prompt_for


class ClosedJsonObject(StoppingCriteria):
    def __init__(self, tokenizer, prompt_length: int) -> None:
        self.tokenizer = tokenizer
        self.prompt_length = prompt_length

    def __call__(self, input_ids, scores, **kwargs) -> bool:
        text = self.tokenizer.decode(input_ids[0][self.prompt_length :], skip_special_tokens=True)
        start = text.find("{")
        if start == -1:
            return False
        depth = 0
        for character in text[start:]:
            if character == "{":
                depth += 1
            elif character == "}":
                depth -= 1
                if depth == 0:
                    return True
        return False


class CausalExtractor:
    def __init__(
        self,
        model_name: str,
        adapter: Path | None = None,
        max_new_tokens: int = 400,
        threads: int | None = None,
        examples: list[tuple[str, str]] | None = None,
    ) -> None:
        if threads:
            torch.set_num_threads(threads)
        self.tokenizer = AutoTokenizer.from_pretrained(str(adapter) if adapter else model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32)
        if adapter is not None:
            from peft import PeftModel

            model = PeftModel.from_pretrained(model, str(adapter))
            model = model.merge_and_unload()
        model.eval()
        self.model = model
        self.max_new_tokens = max_new_tokens
        self.examples = examples or []

    def generate(self, document: str) -> str:
        messages = prompt_for(document, self.examples)
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(text, return_tensors="pt")
        stopping = StoppingCriteriaList(
            [ClosedJsonObject(self.tokenizer, inputs["input_ids"].shape[1])]
        )
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id,
                stopping_criteria=stopping,
            )
        completion = output[0][inputs["input_ids"].shape[1] :]
        return self.tokenizer.decode(completion, skip_special_tokens=True)
