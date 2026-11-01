"""SFX Generator — free AI sound effects + free library picker.

Persistence spec (per Kanta):
  - Favorites are kept even after the site is closed
    -> favorites live in the BROWSER (IndexedDB for generated audio blobs,
       localStorage for library links). The server stores nothing.
  - Everything else disappears
    -> generated files are kept only in this server's RAM and in the page's
       memory. Restart / reload and they are gone.
  - Local download is always available (browser-side <a download>).

Run:  uvicorn app:app --port 8300   (or .venv/bin/python app.py)
"""
import io
import json
import uuid
import wave
from pathlib import Path

import numpy as np
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from gen import ai_engine, procedural, sa3_engine, tangoflux_engine, translate
from gen.presets import PRESETS, preset_for

BASE = Path(__file__).resolve().parent
app = FastAPI(title="SFX Generator")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

JOBS: dict[str, bytes] = {}  # RAM only — by design

# Deliveries are shaped for video work: 48 kHz by default, 44.1 kHz
# selectable (native rate of the AI engines), channels per request.
DELIVERY_SR = 48000
DELIVERY_RATES = (48000, 44100)


def shape_delivery(audio: np.ndarray, sr: int, channels: int,
                   target: int = DELIVERY_SR) -> tuple[np.ndarray, int]:
    """[n] or [ch, n] float audio -> ([channels, n] at target rate, target).

    Resampling uses scipy's polyphase filter (44100->48000 is up 160/down 147,
    16000->48000 is up 3, 48000->44100 is up 147/down 160). When the source
    already matches the target, the audio passes through unresampled.
    A mono source delivered as stereo is dual-mono; a stereo source
    delivered as mono is a plain downmix.
    """
    a = np.asarray(audio, dtype=np.float32)
    if a.ndim == 1:
        a = a[None, :]
    if sr != target:
        from math import gcd

        from scipy.signal import resample_poly
        g = gcd(target, int(sr))
        a = np.stack([resample_poly(ch, target // g, int(sr) // g)
                      for ch in a]).astype(np.float32)
    if channels == 2 and a.shape[0] == 1:
        a = np.concatenate([a, a], axis=0)
    elif channels == 1 and a.shape[0] > 1:
        a = a.mean(axis=0, keepdims=True)
    return a, target


def to_wav_bytes(audio: np.ndarray, sr: int, channels: int = 1,
                 rate: int = DELIVERY_SR) -> bytes:
    a, sr = shape_delivery(audio, sr, channels, rate)
    buf = io.BytesIO()
    pcm = (np.clip(a, -1, 1) * 32767).astype(np.int16)
    with wave.open(buf, "wb") as w:
        w.setnchannels(int(a.shape[0]))
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.T.tobytes())  # interleave channels
    return buf.getvalue()


class GenReq(BaseModel):
    prompt: str
    seconds: float = 3.0
    engine: str = "auto"  # auto | ai | sa3 | tangoflux | synth
    seed: int | None = None
    guidance: float | None = None  # AudioLDM2 guidance_scale (variety lever)
    format: str = "stereo"  # delivery channels: stereo | mono
    rate: int = DELIVERY_SR  # delivery sample rate: 48000 | 44100


@app.get("/", response_class=HTMLResponse)
def index():
    return (BASE / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/api/engines")
def engines():
    return {"ai_audioldm2": ai_engine.available(), "ai_sa3": sa3_engine.available(),
            "ai_tangoflux": tangoflux_engine.available(),
            "synth": True,
            "ai_note": "AudioLDM2 は初回生成時にモデル(~3.5GB)を自動ダウンロードします",
            "sa3_note": "Stable Audio 3 SFX は初回生成時にモデルを自動ダウンロードします（要AIセットアップ）",
            "tf_note": "TangoFlux は初回生成時にモデルを自動ダウンロードします（要AIセットアップ）"}


@app.get("/api/presets")
def presets():
    return PRESETS


@app.get("/api/library")
def library():
    return json.loads((BASE / "data" / "library.json").read_text(encoding="utf-8"))


@app.post("/api/generate")
def generate(req: GenReq):
    preset = preset_for(req.prompt)
    engine = req.engine
    used = None
    audio = None
    sr = procedural.SR
    # No explicit seed -> roll a fresh one each time, so retrying the same
    # prompt gives a different take instead of the identical sound.
    seed = req.seed if req.seed is not None else int(uuid.uuid4().int % 1_000_000)
    guidance = req.guidance if req.guidance is not None else 3.5
    prompt_en = preset["en"] if preset else (translate.to_english(req.prompt) or req.prompt)
    channels = 2 if req.format == "stereo" else 1
    rate = req.rate if req.rate in DELIVERY_RATES else DELIVERY_SR
    if engine == "sa3":
        if not sa3_engine.available():
            return {"ok": False, "error": "Stable Audio 3 が未セットアップです（AIセットアップを実行してください）"}
        try:
            audio, sr = sa3_engine.generate(prompt_en, dur=req.seconds, seed=seed)
            used = "sa3-small-sfx"
        except Exception as e:
            return {"ok": False, "error": f"Stable Audio 3 の生成に失敗しました: {e}"}
    elif engine == "tangoflux":
        if not tangoflux_engine.available():
            return {"ok": False, "error": "TangoFlux が未セットアップです（AIセットアップを実行してください）"}
        try:
            audio, sr = tangoflux_engine.generate(prompt_en, dur=req.seconds, seed=seed)
            used = "tangoflux"
        except Exception as e:
            return {"ok": False, "error": f"TangoFlux の生成に失敗しました: {e}"}
    elif engine in ("auto", "ai") and ai_engine.available():
        try:
            audio = ai_engine.generate(prompt_en, dur=min(req.seconds, 10.24), seed=seed,
                                       guidance=guidance)
            sr = ai_engine.SAMPLE_RATE
            used = "audioldm2"
        except Exception as e:
            if engine == "ai":
                return {"ok": False, "error": f"AI生成に失敗しました: {e}"}
            audio = None  # fall through to synth
    if audio is None:
        audio, recipe = procedural.synthesize(req.prompt, dur=req.seconds, seed=seed)
        used = f"synth:{recipe}"
    job = uuid.uuid4().hex[:12]
    JOBS[job] = to_wav_bytes(np.asarray(audio, dtype=np.float32), sr, channels, rate)
    return {"ok": True, "id": job, "url": f"/api/file/{job}",
            "engine_used": used, "sample_rate": rate, "channels": channels,
            "seed": seed, "guidance": guidance,
            "prompt_used": prompt_en if used in ("audioldm2", "sa3-small-sfx", "tangoflux") else req.prompt}


@app.get("/api/file/{job}")
def file(job: str):
    data = JOBS.get(job)
    if data is None:
        return Response(status_code=404, content="gone (by design: files live in RAM only)")
    return Response(content=data, media_type="audio/wav")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8300)
