"""TangoFlux worker — runs INSIDE the TangoFlux venv (launched as a
subprocess by gen/tangoflux_engine.py). Never imported by the app server.

Loads declare-lab/TangoFlux, generates one clip, writes a 16-bit WAV
(interleaved) via the stdlib wave module, and prints one JSON line with
the output's sample rate / channels / frames.
"""
import argparse
import json
import wave

import numpy as np


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--seconds", type=float, default=10.0)
    ap.add_argument("--seed", type=int, default=-1)
    ap.add_argument("--steps", type=int, default=50)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    import torch

    if a.seed >= 0:
        torch.manual_seed(int(a.seed))

    device = "cpu"
    if torch.cuda.is_available():
        device = "cuda"
    elif getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        device = "mps"

    from tangoflux import TangoFluxInference

    model = TangoFluxInference(name="declare-lab/TangoFlux", device=device)
    # Same recipe as TangoFluxInference.generate(), but the T5 text
    # encoder (~3 GB in fp32) is released after the diffusion flow and
    # before the VAE decode: on small-RAM machines (<=8 GB, no swap)
    # the stock generate() gets OOM-killed at the decode step, after
    # all diffusion steps have already completed.
    import gc

    with torch.no_grad():
        latents = model.model.inference_flow(
            a.prompt,
            duration=float(a.seconds),
            num_inference_steps=int(a.steps),
            guidance_scale=4.5,
        )
        # Decode needs only the VAE. Free the T5 text encoder AND the
        # DiT itself, and return the freed heap to the OS: freeing T5
        # alone was not enough (the worker was still OOM-killed at
        # decode), because the allocator kept the pages and the DiT
        # (~2 GB fp32) stayed resident next to the VAE.
        vae = model.vae
        sr = int(model.vae.config.sampling_rate)
        try:
            model.model.text_encoder = None
        except Exception:
            pass
        try:
            model.model = None
        except Exception:
            pass
        gc.collect()
        try:
            import ctypes
            ctypes.CDLL("libc.so.6").malloc_trim(0)
        except Exception:
            pass
        wave_t = vae.decode(latents.transpose(2, 1)).sample.cpu()[0]
    wave_t = wave_t[:, : int(float(a.seconds) * sr)]
    arr = wave_t.detach().cpu().numpy() if hasattr(wave_t, "detach") else np.asarray(wave_t)
    arr = np.asarray(arr, dtype=np.float32)
    if arr.ndim == 3:  # (batch, ch, n)
        arr = arr[0]
    if arr.ndim == 1:
        arr = arr[None, :]
    arr = np.clip(arr, -1.0, 1.0)
    pcm = (arr * 32767).astype(np.int16)
    with wave.open(a.out, "wb") as w:
        w.setnchannels(int(arr.shape[0]))
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.T.tobytes())  # interleave channels
    print(json.dumps({"sample_rate": sr, "channels": int(arr.shape[0]),
                      "frames": int(arr.shape[1])}))


if __name__ == "__main__":
    main()
