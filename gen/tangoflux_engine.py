"""TangoFlux engine (declare-lab — Apache 2.0, no agreement / no gating).

Reserve engine behind Stable Audio 3: same subprocess-isolation pattern
as gen/sa3_engine.py, because TangoFlux pins its own stack
(torch 2.4 / transformers 4.44 / diffusers 0.30) which must not disturb
the AudioLDM2 pins. The upstream repo is cloned into `tangoflux/` next
to this project (setup script does it), with its own `.venv`; generation
runs gen/tangoflux_worker.py with that venv's python.

Native output: stereo 44.1 kHz, up to 30 s. app.py resamples deliveries
to 48 kHz and shapes the channels (stereo / mono) for video work.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent.parent
TF_HOME = Path(os.environ.get("SFX_TF_HOME", BASE / "tangoflux"))
WORKER = Path(__file__).resolve().parent / "tangoflux_worker.py"
NATIVE_SR = 44100
MAX_SECONDS = 30.0


def _python() -> Path | None:
    for cand in (TF_HOME / ".venv" / "bin" / "python",
                 TF_HOME / ".venv" / "Scripts" / "python.exe"):
        if cand.exists():
            return cand
    return None


def available() -> bool:
    return _python() is not None and (TF_HOME / "tangoflux").is_dir()


def _read_wav(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as w:
        ch, sr, n = w.getnchannels(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    pcm = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    return pcm.reshape(-1, ch).T.copy(), sr  # [ch, frames]


def generate(prompt_en: str, dur: float = 10.0, seed: int | None = None,
             steps: int = 50) -> tuple[np.ndarray, int]:
    """Returns ([channels, samples] float32, sample_rate). Raises on failure."""
    py = _python()
    if py is None:
        raise RuntimeError("TangoFlux environment not installed (run the AI setup)")
    dur = float(np.clip(dur, 1.0, MAX_SECONDS))
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "tf.wav"
        cmd = [str(py), str(WORKER), "--prompt", prompt_en,
               "--seconds", str(dur), "--seed", str(-1 if seed is None else int(seed)),
               "--steps", str(int(steps)), "--out", str(out)]
        env = dict(os.environ, PYTHONPATH=str(TF_HOME))
        proc = subprocess.run(cmd, cwd=str(TF_HOME), env=env, capture_output=True,
                              text=True, timeout=3600)
        if proc.returncode != 0 or not out.exists():
            tail = (proc.stderr or proc.stdout or "")[-800:]
            raise RuntimeError(f"TangoFlux generation failed: {tail}")
        return _read_wav(out)
