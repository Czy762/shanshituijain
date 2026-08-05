import os
import json
from typing import Optional

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
USE_OPENAI = bool(OPENAI_API_KEY)
LOCAL_MODEL_NAME = os.environ.get("LOCAL_MODEL_NAME", "gpt2")  # default small model for local demo

# External OpenAI wrapper
def generate_with_openai(prompt: str, max_tokens: int = 150, temperature: float = 0.2) -> str:
    try:
        import openai
    except Exception:
        raise RuntimeError("openai package not installed")
    openai.api_key = OPENAI_API_KEY
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini" if False else "gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return resp['choices'][0]['message']['content'].strip()

# Local HuggingFace wrapper
_def_local_generator = None

def _init_local_generator():
    global _def_local_generator
    if _def_local_generator is not None:
        return _def_local_generator
    try:
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        import torch
    except Exception as e:
        raise RuntimeError("transformers/torch not available for local generation: " + str(e))
    tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_NAME, use_fast=False)
    model = AutoModelForCausalLM.from_pretrained(LOCAL_MODEL_NAME, device_map='auto', torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
    gen = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map='auto')
    _def_local_generator = gen
    return _def_local_generator

def generate_with_local(prompt: str, max_new_tokens: int = 150, temperature: float = 0.2) -> str:
    gen = _init_local_generator()
    out = gen(prompt, max_new_tokens=max_new_tokens, do_sample=temperature>0, temperature=temperature)
    # pipeline returns list of dicts with 'generated_text'
    return out[0]['generated_text']

# Unified generate function
def generate_text(prompt: str, backend: Optional[str] = None, **kwargs) -> str:
    backend = backend or ("openai" if USE_OPENAI else "local")
    if backend == "openai":
        if not USE_OPENAI:
            raise RuntimeError("OpenAI not configured")
        return generate_with_openai(prompt, **kwargs)
    elif backend == "local":
        return generate_with_local(prompt, **kwargs)
    else:
        raise ValueError("unknown backend")
