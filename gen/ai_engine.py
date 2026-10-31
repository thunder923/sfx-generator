"""Free AI text-to-SFX engine: AudioLDM2 (cvssp/audioldm2, via diffusers).

Fully free / local / no API key. First use downloads the model (~3.5 GB)
from Hugging Face. Native output is 16 kHz mono — fine for SFX previews;
the app upsamples on delivery if needed. CPU works (slow: ~1-3 min for
10 s), Apple Silicon MPS / NVIDIA CUDA are used automatically when present.

Install:  pip install torch diffusers transformers accelerate scipy
(torch CPU wheel: pip install torch --index-url https://download.pytorch.org/whl/cpu)
"""
from __future__ import annotations

import numpy as np

_pipe = None
MODEL_ID = "cvssp/audioldm2"
SAMPLE_RATE = 16000


def available() -> bool:
    try:
        import torch  # noqa: F401
        import diffusers  # noqa: F401
        return True
    except Exception:
        return False


def _load():
    global _pipe
    if _pipe is not None:
        return _pipe
    import torch
    from diffusers import AudioLDM2Pipeline
    device = "cuda" if torch.cuda.is_available() else (
        "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else "cpu")
    dtype = torch.float16 if device == "cuda" else torch.float32
    pipe = AudioLDM2Pipeline.from_pretrained(MODEL_ID, torch_dtype=dtype)
    _pipe = pipe.to(device)
    return _pipe


def generate(prompt_en: str, dur: float = 5.0, seed: int | None = None,
             guidance: float = 3.5) -> np.ndarray:
    import torch
    pipe = _load()
    device = next(pipe.unet.parameters()).device
    gen = torch.Generator(device.type).manual_seed(int(seed) if seed is not None else 42)
    out = pipe(
        prompt_en,
        negative_prompt="low quality, music, speech, voice",
        num_inference_steps=100 if device.type == "cpu" else 200,
        audio_length_in_s=float(np.clip(dur, 1.0, 10.24)),
        guidance_scale=float(guidance),
        generator=gen,
    )
    return np.asarray(out.audios[0], dtype=np.float32)
