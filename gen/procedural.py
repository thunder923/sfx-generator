"""Procedural SFX synth — the always-available fallback engine.

Used until (or unless) the AudioLDM2 AI engine is installed. Each recipe is
a classic DSP synthesis for one sound family. Output: float32 mono at 48 kHz
(the web layer may downsample for the AI engine, which is 16 kHz native).
"""
from __future__ import annotations

import numpy as np
from scipy import signal as sp

SR = 48000


def _env(n: int, attack: float = 0.01, decay_exp: float = 3.0) -> np.ndarray:
    t = np.linspace(0, 1, n)
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-decay_exp * t)


def _noise(rng, n):
    return rng.standard_normal(n).astype(np.float32)


def _lowpass(x, freq, sr=SR):
    sos = sp.butter(2, freq, btype="lowpass", fs=sr, output="sos")
    return sp.sosfiltfilt(sos, x).astype(np.float32)


def _highpass(x, freq, sr=SR):
    sos = sp.butter(2, freq, btype="highpass", fs=sr, output="sos")
    return sp.sosfiltfilt(sos, x).astype(np.float32)


def explosion(rng, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * (60 * np.exp(-3 * t) + 30) * t) * np.exp(-2.5 * t)
    blast = _lowpass(_noise(rng, n), 900) * np.exp(-4 * t)
    return (boom * 0.9 + blast * 0.7).astype(np.float32)


def rain(rng, dur):
    n = int(dur * SR)
    base = _highpass(_lowpass(_noise(rng, n), 6000), 1200) * 0.25
    drops = np.zeros(n, dtype=np.float32)
    for _ in range(int(dur * 220)):
        i = rng.integers(0, n - 800)
        f = rng.uniform(1800, 4200)
        seg = np.sin(2 * np.pi * f * np.arange(400) / SR) * np.exp(-np.arange(400) / 60)
        drops[i:i + 400] += seg * rng.uniform(0.05, 0.3)
    return (base + drops).astype(np.float32)


def wind(rng, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    gust = 0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + 1.2 * np.sin(2 * np.pi * 0.041 * t))
    return (_lowpass(_noise(rng, n), 480) * gust * 1.4).astype(np.float32)


def thunder(rng, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    crack = _noise(rng, n) * np.exp(-30 * t) * 0.8
    rumble = _lowpass(_noise(rng, n), 160) * np.exp(-0.9 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.3 * t))
    return (crack + rumble * 1.6).astype(np.float32)


def waves(rng, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    cycle = np.maximum(np.sin(2 * np.pi * t / max(dur / 2.2, 1.0)), 0) ** 2
    return (_lowpass(_noise(rng, n), 900) * cycle * 0.9).astype(np.float32)


def beep(rng, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    step = max(int(SR * 0.22), 1)
    for i, f in enumerate([880, 1174, 1568]):
        a = i * step * 2
        if a < n:
            seg = np.sin(2 * np.pi * f * t[: n - a]) * _env(n - a, 0.005, 6)
            out[a:] += seg * 0.4
    return out


def chime(rng, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    for f, delay, amp in [(1567, 0.0, 0.5), (2093, 0.18, 0.35), (2637, 0.36, 0.25)]:
        a = int(delay * SR)
        if a < n:
            out[a:] += np.sin(2 * np.pi * f * t[: n - a]) * np.exp(-2.2 * t[: n - a]) * amp
    return out


def knock(rng, dur):
    n = int(dur * SR); out = np.zeros(n, dtype=np.float32)
    for start in (0.05, 0.45):
        a = int(start * SR)
        seg_n = min(int(0.09 * SR), n - a)
        if seg_n <= 0:
            continue
        t = np.arange(seg_n) / SR
        out[a:a + seg_n] += np.sin(2 * np.pi * 180 * t) * np.exp(-60 * t) * 0.9
        out[a:a + seg_n] += _lowpass(_noise(rng, seg_n), 2500) * np.exp(-90 * t) * 0.4
    return out


def footsteps(rng, dur):
    n = int(dur * SR); out = np.zeros(n, dtype=np.float32)
    step_every = 0.42
    for s in np.arange(0.1, dur - 0.15, step_every):
        a = int(s * SR); seg_n = min(int(0.11 * SR), n - a)
        if seg_n <= 0:
            continue
        t = np.arange(seg_n) / SR
        out[a:a + seg_n] += _lowpass(_noise(rng, seg_n), 700) * np.exp(-35 * t) * 0.8
    return out


def droplet(rng, dur):
    n = int(dur * SR); out = np.zeros(n, dtype=np.float32)
    for s in np.arange(0.1, dur - 0.2, 0.55):
        a = int(s * SR); seg_n = min(int(0.12 * SR), n - a)
        if seg_n <= 0:
            continue
        t = np.arange(seg_n) / SR
        f = 1400 * np.exp(-6 * t) + 700
        ph = np.cumsum(2 * np.pi * f / SR)
        out[a:a + seg_n] += np.sin(ph) * np.exp(-25 * t) * 0.5
    return out


def sword(rng, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 5000 * np.exp(-4 * t) + 600
    ph = np.cumsum(2 * np.pi * f / SR)
    whoosh = _highpass(_noise(rng, n), 1500) * _env(n, 0.08, 2.0)
    ring = np.sin(ph) * np.exp(-3 * t) * 0.25
    return (whoosh * 0.6 + ring).astype(np.float32)


def magic(rng, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    scale = [1568, 1760, 2093, 2349, 2637, 3136]
    for i in range(14):
        a = int(rng.uniform(0, max(dur - 0.4, 0.1)) * SR)
        seg_n = min(int(0.35 * SR), n - a)
        if seg_n <= 0:
            continue
        f = scale[rng.integers(0, len(scale))]
        ts = np.arange(seg_n) / SR
        out[a:a + seg_n] += np.sin(2 * np.pi * f * ts) * np.exp(-9 * ts) * 0.22
    return out


RECIPES = {
    "explosion": explosion, "rain": rain, "wind": wind, "thunder": thunder,
    "waves": waves, "beep": beep, "chime": chime, "knock": knock,
    "footsteps": footsteps, "droplet": droplet, "sword": sword, "magic": magic,
}

# Japanese / English keyword -> recipe
KEYWORDS = [
    (["爆発", "爆弾", "explosion", "bomb"], "explosion"),
    (["雨", "rain"], "rain"),
    (["風", "wind", "storm"], "wind"),
    (["雷", "thunder", "lightning"], "thunder"),
    (["波", "海", "waves", "ocean", "sea"], "waves"),
    (["ビープ", "電子音", "beep", "決定音", "クリック音"], "beep"),
    (["チャイム", "ベル", "chime", "bell", "通知音"], "chime"),
    (["ノック", "ドア", "knock", "door"], "knock"),
    (["足音", "歩く", "footstep", "walk"], "footsteps"),
    (["水滴", "しずく", "droplet", "water drop"], "droplet"),
    (["剣", "刀", "斬撃", "sword", "slash"], "sword"),
    (["魔法", "キラキラ", "magic", "sparkle"], "magic"),
]


def match_recipe(prompt: str) -> str | None:
    p = prompt.lower()
    for keys, name in KEYWORDS:
        if any(k.lower() in p for k in keys):
            return name
    return None


def synthesize(prompt: str, dur: float = 3.0, seed: int | None = None) -> tuple[np.ndarray, str]:
    rng = np.random.default_rng(seed)
    name = match_recipe(prompt) or "magic"
    audio = RECIPES[name](rng, float(np.clip(dur, 0.3, 30.0)))
    peak = np.max(np.abs(audio)) + 1e-9
    if peak > 0.89:
        audio = audio * (0.89 / peak)
    return audio.astype(np.float32), name
