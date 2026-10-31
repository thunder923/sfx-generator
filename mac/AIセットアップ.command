#!/bin/zsh
# 効果音ジェネレーター — Mac用 AIフルセットアップ
# AIエンジン（AudioLDM2）込みで全部入れるための一括スクリプト。
# ダブルクリックで実行。モデルDLに失敗しても最後まで進み、結果を表示します。
#
# ⚠️ Python は 3.12 / 3.13 が必須 (2026-10-31 判明):
#    transformers==4.46.3 が要求する tokenizers 0.20.x は Python 3.14 用の
#    ホイールが無く、ソースビルドも PyO3 の対応上限 (3.13) で失敗する。
#    そのためこのスクリプトは 3.12 を探し、無ければ Homebrew で入れて、
#    .venv を 3.12 で作り直す (既存の .venv は消さずにリネームして退避)。

cd "$(dirname "$0")/.." || exit 1
echo "=== 効果音ジェネレーター: AIセットアップ開始 ==="
echo "作業フォルダ: $(pwd)"
echo

# 0) Python 3.12 / 3.13 を探す (無ければ Homebrew で 3.12 を入れる)
find_py() {
  local v cand
  for v in 3.12 3.13; do
    for cand in "/opt/homebrew/opt/python@$v/bin/python$v" "/usr/local/opt/python@$v/bin/python$v"; do
      [ -x "$cand" ] && { echo "$cand"; return 0; }
    done
    command -v "python$v" >/dev/null 2>&1 && { command -v "python$v"; return 0; }
  done
  return 1
}
BASE_PY="$(find_py)"
if [ -z "$BASE_PY" ] && command -v brew >/dev/null 2>&1; then
  echo "--- Python 3.12 が無いので Homebrew でインストールします（数分かかります）---"
  brew install python@3.12
  BASE_PY="$(find_py)"
  echo
fi
if [ -z "$BASE_PY" ]; then
  echo "❌ Python 3.12 / 3.13 が見つかりませんでした。"
  echo "   先にターミナルで次を実行してから、このセットアップをもう一度開いてください:"
  echo "     brew install python@3.12"
  read -r "?Enterキーで閉じます: "
  exit 1
fi
echo "使用する Python: $BASE_PY ($($BASE_PY --version 2>&1))"
echo

# 1) 仮想環境 (バージョンが 3.12/3.13 でない既存 .venv は退避して作り直す)
if [ -d .venv ]; then
  CUR_VER="$(.venv/bin/python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null)"
  if [ "$CUR_VER" = "3.12" ] || [ "$CUR_VER" = "3.13" ]; then
    echo "--- .venv は既にあります（Python $CUR_VER、そのまま使います）---"
  else
    BAK=".venv.bak-py${CUR_VER:-unknown}"
    [ -e "$BAK" ] && BAK="${BAK}-$(date +%H%M%S)"
    echo "--- 既存の .venv は Python ${CUR_VER:-不明} のため $BAK へ退避し、$BASE_PY で作り直します ---"
    mv .venv "$BAK"
    "$BASE_PY" -m venv .venv
  fi
else
  echo "--- .venv を作成します ---"
  "$BASE_PY" -m venv .venv
fi
PIP=".venv/bin/pip"
PY=".venv/bin/python"
"$PIP" install -q --upgrade pip
echo

# 2) 基本ライブラリ
echo "--- 基本ライブラリをインストールします（fastapi / uvicorn など）---"
"$PIP" install fastapi uvicorn pydantic numpy scipy
echo

# 3) PyTorch（Mac通常版をそのまま入れる）
echo "--- PyTorch をインストールします（少し時間がかかります）---"
"$PIP" install torch
echo

# 4) AudioLDM2 用ライブラリ
# 版数固定が必須: transformers v5 では AudioLDM2 が使う GPT2 生成APIが無くなり動かないため
echo "--- AudioLDM2 用ライブラリをインストールします（diffusers / transformers / accelerate）---"
"$PIP" install diffusers==0.30.3 transformers==4.46.3 accelerate
echo

# 4.5) 導入チェック (入ったかどうかを必ず確認してから次へ)
echo "--- 導入チェック ---"
if "$PY" - <<'PYEOF'
import torch, diffusers, transformers
print(f"torch {torch.__version__} / diffusers {diffusers.__version__} / transformers {transformers.__version__}")
print("MPS (Apple Silicon GPU):", torch.backends.mps.is_available())
PYEOF
then
  AI_OK=1
  echo "✅ AIライブラリの導入 OK"
else
  AI_OK=0
  echo "❌ AIライブラリが入っていません（上のエラーを確認してください）。"
  echo "   モデルのダウンロードはスキップします。"
fi
echo

# 5) モデルの先行ダウンロード（cvssp/audioldm2、約3.5GB）
if [ "$AI_OK" = "1" ]; then
  echo "--- AudioLDM2 モデルを先にダウンロードします（約3.5GB、時間がかかります）---"
  if "$PY" - <<'PYEOF'
from huggingface_hub import snapshot_download
path = snapshot_download("cvssp/audioldm2")
print("ダウンロード完了:", path)
PYEOF
  then
    echo "✅ AudioLDM2 モデルのダウンロード完了"
  else
    echo "⚠️ モデルの先行ダウンロードに失敗しました（上のエラーが原因です。ネット接続も確認してください）。"
    echo "   初回生成時にも自動でダウンロードされるので、このまま進んでも大丈夫です。"
  fi
  echo
fi

echo "=== セットアップ完了 ==="
if [ "$AI_OK" = "1" ]; then
  echo "AIエンジン（AudioLDM2）: 利用可能になっています。"
else
  echo "AIエンジン（AudioLDM2）: まだ使えません（簡易シンセでの生成は可能です）。"
fi
echo "「一発起動.command」をダブルクリックするとアプリが Safari で開きます。"
echo "このウィンドウは閉じてOKです。"
read -r "?Enterキーで閉じます: "
