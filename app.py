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

from gen import ai_engine, procedural
from gen.presets import PRESETS, preset_for

BASE = Path(__file__).resolve().parent
app = FastAPI(title="SFX Generator")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

JOBS: dict[str, bytes] = {}  # RAM only — by design


def to_wav_bytes(audio: np.ndarray, sr: int) -> bytes:
    buf = io.BytesIO()
    pcm = (np.clip(audio, -1, 1) * 32767).astype(np.int16)
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return buf.getvalue()


class GenReq(BaseModel):
    prompt: str
    seconds: float = 3.0
    engine: str = "auto"  # auto | ai | synth
    seed: int | None = None


@app.get("/", response_class=HTMLResponse)
def index():
    return (BASE / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/api/engines")
def engines():
    return {"ai_audioldm2": ai_engine.available(), "synth": True,
            "ai_note": "AudioLDM2 は初回生成時にモデル(~3.5GB)を自動ダウンロードします"}


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
    if engine in ("auto", "ai") and ai_engine.available():
        try:
            prompt_en = preset["en"] if preset else req.prompt
            audio = ai_engine.generate(prompt_en, dur=min(req.seconds, 10.24), seed=req.seed)
            sr = ai_engine.SAMPLE_RATE
            used = "audioldm2"
        except Exception as e:
            if engine == "ai":
                return {"ok": False, "error": f"AI生成に失敗しました: {e}"}
            audio = None  # fall through to synth
    if audio is None:
        audio, recipe = procedural.synthesize(req.prompt, dur=req.seconds, seed=req.seed)
        used = f"synth:{recipe}"
    job = uuid.uuid4().hex[:12]
    JOBS[job] = to_wav_bytes(np.asarray(audio, dtype=np.float32), sr)
    return {"ok": True, "id": job, "url": f"/api/file/{job}",
            "engine_used": used, "sample_rate": sr}


@app.get("/api/file/{job}")
def file(job: str):
    data = JOBS.get(job)
    if data is None:
        return Response(status_code=404, content="gone (by design: files live in RAM only)")
    return Response(content=data, media_type="audio/wav")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8300)
