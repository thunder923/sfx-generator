"""Stable Audio 3 worker — runs INSIDE the SA3 venv (launched as a
subprocess by gen/sa3_engine.py). Never imported by the app server.

Loads Stable Audio 3 Small SFX, generates one clip, writes a 16-bit WAV
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
    ap.add_argument("--cfg", type=float, default=1.0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    from stable_audio_3 import StableAudioModel

    model = StableAudioModel.from_pretrained("small-sfx")
    audio = model.generate(
        prompt=a.prompt,
        duration=float(a.seconds),
        steps=8,
        cfg_scale=float(a.cfg),
        seed=int(a.seed),
    )
    sr = int(getattr(model, "sample_rate", 44100))
    t = audio
    if isinstance(t, (tuple, list)):  # tolerate (waveform, sample_rate)
        if len(t) == 2 and isinstance(t[1], (int, float)):
            t, sr = t[0], int(t[1])
        else:
            t = t[0]
    arr = t.detach().cpu().numpy() if hasattr(t, "detach") else np.asarray(t)
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
