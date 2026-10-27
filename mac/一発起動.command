#!/bin/zsh
# 効果音ジェネレーター — Macランチャー（Web版と同じサーバーをローカル起動し Safari で開く）
cd "$(dirname "$0")/.."
PORT=8300
URL="http://localhost:${PORT}"

if curl -s -o /dev/null --max-time 2 "$URL"; then
  open -a Safari "$URL"
  exit 0
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -q fastapi uvicorn pydantic numpy scipy
  # AIエンジン（無料・任意）を使う場合:
  # .venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu
  # .venv/bin/pip install diffusers transformers accelerate
fi

nohup .venv/bin/python app.py > sfx.log 2>&1 &
for i in {1..30}; do
  if curl -s -o /dev/null --max-time 2 "$URL"; then break; fi
  sleep 1
done
open -a Safari "$URL"
