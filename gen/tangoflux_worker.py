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
    wave_t = model.generate(
        a.prompt,
        steps=int(a.steps),
        duration=float(a.seconds),
    )
    sr = 44100
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
