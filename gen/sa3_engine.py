"""Stable Audio 3 Small SFX engine (Stability AI — free, Community License).

Why subprocess isolation: SA3 ships its own stack (torch 2.7 + its own
lockfile) which must not disturb the pinned diffusers/transformers pair
that AudioLDM2 needs. The official repo is cloned into `sa3/` next to
this project (setup script does it), with its own `.venv`; generation
runs gen/sa3_worker.py with that venv's python.

Native output: stereo 44.1 kHz, variable length up to 120 s — built for
foley and ambience, the two things AudioLDM2 (16 kHz mono, ~10 s) is
weak at. app.py resamples deliveries to 48 kHz and shapes the channels
(stereo / mono) for video work.
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
SA3_HOME = Path(os.environ.get("SFX_SA3_HOME", BASE / "sa3"))
WORKER = Path(__file__).resolve().parent / "sa3_worker.py"
NATIVE_SR = 44100
MAX_SECONDS = 120.0


def _python() -> Path | None:
    for cand in (SA3_HOME / ".venv" / "bin" / "python",
                 SA3_HOME / ".venv" / "Scripts" / "python.exe"):
        if cand.exists():
            return cand
    return None


def available() -> bool:
    return _python() is not None and (SA3_HOME / "stable_audio_3").is_dir()


def _read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as w:
        ch, sr, n = w.getnchannels(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return pcm.reshape(-1, ch).T.copy(), sr  # [ch, frames]


def generate(prompt_en: str, dur: float = 10.0, seed: int | None = None,
             cfg: float = 1.0) -> tuple[np.ndarray, int]:
    """Returns ([channels, samples] float32, sample_rate). Raises on failure."""
    py = _python()
    if py is None:
        raise RuntimeError("SA3 environment not installed (run the AI setup)")
    dur = float(np.clip(dur, 1.0, MAX_SECONDS))
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "sa3.wav"
        cmd = [str(py), str(WORKER), "--prompt", prompt_en,
               "--seconds", str(dur), "--seed", str(-1 if seed is None else int(seed)),
               "--cfg", str(cfg), "--out", str(out)]
        env = dict(os.environ, PYTHONPATH=str(SA3_HOME))
        proc = subprocess.run(cmd, cwd=str(SA3_HOME), env=env, capture_output=True,
                              text=True, timeout=3600)
        if proc.returncode != 0 or not out.exists():
            tail = (proc.stderr or proc.stdout or "")[-800:]
            raise RuntimeError(f"SA3 generation failed: {tail}")
        return _read_wav(out)
