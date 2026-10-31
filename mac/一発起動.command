#!/bin/zsh
# 効果音ジェネレーター — Macランチャー（Web版と同じサーバーをローカル起動し Safari で開く）
cd "$(dirname "$0")/.."
PORT=8300
URL="http://localhost:${PORT}"

# 起動済みサーバーがあっても、venv やコードの更新を反映するため必ず作り直す
# （旧仕様は「応答したら開くだけ」で、古い venv のサーバーが残り続け AI 未導入判定になる事故があった）
for p in $(lsof -ti tcp:${PORT} -sTCP:LISTEN 2>/dev/null); do kill $p; done
sleep 1

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
