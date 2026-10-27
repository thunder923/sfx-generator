#!/bin/zsh
# 効果音ジェネレーター — Mac用 AIフルセットアップ
# AIエンジン（AudioLDM2）込みで全部入れるための一括スクリプト。
# ダブルクリックで実行。モデルDLに失敗しても最後まで進み、結果を表示します。

cd "$(dirname "$0")/.." || exit 1
echo "=== 効果音ジェネレーター: AIセットアップ開始 ==="
echo "作業フォルダ: $(pwd)"
echo

# 1) 仮想環境
if [ ! -d .venv ]; then
  echo "--- .venv を作成します ---"
  python3 -m venv .venv
else
  echo "--- .venv は既にあります（そのまま使います）---"
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

# 5) モデルの先行ダウンロード（cvssp/audioldm2、約3.5GB）
echo "--- AudioLDM2 モデルを先にダウンロードします（約3.5GB、時間がかかります）---"
if "$PY" - <<'PYEOF'
from huggingface_hub import snapshot_download
path = snapshot_download("cvssp/audioldm2")
print("ダウンロード完了:", path)
PYEOF
then
  echo "✅ AudioLDM2 モデルのダウンロード完了"
else
  echo "⚠️ モデルの先行ダウンロードに失敗しました（ネット接続を確認してください）。"
  echo "   初回生成時にも自動でダウンロードされるので、このまま進んでも大丈夫です。"
fi
echo

echo "=== セットアップ完了 ==="
echo "「一発起動.command」をダブルクリックするとアプリが Safari で開きます。"
echo "このウィンドウは閉じてOKです。"
read -r "?Enterキーで閉じます: "
