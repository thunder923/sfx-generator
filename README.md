# 効果音ジェネレーター — SFX Generator

無料AIで効果音を作る＋フリー音源から選べる、Webアプリ（Macでは .command で起動）。

## Kanta指定の保持仕様（実装済み・要確認ポイント）
- **お気に入りだけ保持**: お気に入りはブラウザ側に保存（生成音は IndexedDB、ライブラリ音源は localStorage）→ **サイトを閉じても残る**
- **それ以外は消える**: 生成結果はサーバーのメモリ(RAM)と画面上だけに存在 → リロード／サーバー再起動で消える。サーバーはディスクに何も書かない
- **ローカルにダウンロード可**: 全アイテムに ⬇ DL ボタン

## 2つの生成エンジン
| エンジン | 内容 | 状態 |
|---|---|---|
| AI（AudioLDM2） | 無料・ローカル・APIキー不要の text-to-audio モデル（cvssp/audioldm2、diffusers）。日本語プリセットは英語プロンプトに翻訳済み。初回はモデル約3.5GBを自動DL。CPUだと10秒生成に数分、Mac(Apple Silicon MPS)／GPU推奨 | ✅ 実生成まで検証済み（2026-10-27）: 「爆発」5秒を生成成功（RMS 0.114 / peak 0.744）。このVMのCPUでは生成約5分。サンプル: `sample_audioldm2_explosion.wav`。バージョン固定が必須（下記 requirements 参照: diffusers 0.30.3 + transformers 4.46.3） |
| 簡易シンセ | DSP合成レシピ12種（爆発／雨／風／雷／波／ビープ／チャイム／ノック／足音／水滴／剣／魔法）。即時生成 | ✅ 動作検証済み |

## フリー音源ライブラリ
- 出典: [プロ生 無料素材 (sounds.pronama.jp)](https://sounds.pronama.jp/) / [VSQ plus+](https://vsq.co.jp/plus/)
- 収録アイテム（試聴／DL／お気に入り可、直接mp3 URLを実在確認済み）:
  プロ生 無料素材（ゲームBGM）21件 ＋ HSP3 無料素材（効果音34件＋BGM 18件）
- リンク収録（件数が膨大なためカテゴリー別リンクをアプリ内に表示し、元サイトで試聴・DL）:
  Adobe Audition Sound Effects（プロ生経由）/ VSQ plus+（全1,726種類・商用可・表記不要、素材そのものの再配布・販売は禁止）
- 利用条件は出典・カテゴリーで違うので、使う前に必ず元サイトで条件確認（アプリ内にも明記＋リンク）
- カタログの再生成は `data/build_library.py`（アイテム追加はそこへ足して実行）

## 起動
```
.venv/bin/python app.py        # http://localhost:8300
# Mac: mac/一発起動.command（Safariで開く）
```

## 使い方（要約）
1. AI生成: 作りたい音を入力（プリセットは日本語OK、自由入力は英語推奨）→
   長さとエンジンを選んで「生成する」。AI は初回のみモデル約3.5GBを自動DL
2. フリー音源ライブラリ: キーワード検索 → 試聴／DL。利用条件は元サイトで確認
3. 残したい音は ⬇ DL か ☆ お気に入り（保持されるのはお気に入りだけ）

同じ内容はアプリ内の「📖 使い方」タブからも読めます。

## プライバシーポリシー（要約・アプリ内に全文表示あり）
- **生成はすべてローカル処理**です。プロンプトや生成音が外部サーバーへ
  送信されることはありません。
- AI モデル（AudioLDM2）使用時のみ、初回生成時にモデル本体（約3.5GB）を
  Hugging Face から自動ダウンロードします（`gen/ai_engine.py` の
  `from_pretrained("cvssp/audioldm2")`）。プロンプト等は送信されません。
- お気に入りはブラウザ内（生成音は IndexedDB、ライブラリは localStorage）に
  保存。サーバーは生成結果を RAM に持つだけで、ディスクに何も書きません。
- ライブラリ音源は出典サイト（プロ生 無料素材）のサーバーからブラウザが
  直接読み込んで再生します。ライブラリを開くと出典サイトへアクセスします。
- 作者への送信・利用状況の収集はありません。
- サーバーは `0.0.0.0:8300` で待ち受け、認証はないため、信頼できる
  ネットワーク（自宅 LAN / Tailscale）の中だけで使う前提です。

## AIエンジンの入れ方（Mac想定・VMで検証済みの組み合わせ）
**Python は 3.12 / 3.13 が必須**（2026-10-31 判明）: transformers==4.46.3 が要求する
tokenizers 0.20.x は Python 3.14 用ホイールが無く、ソースビルドも PyO3 の対応上限
（3.13）で失敗する。Mac の `mac/AIセットアップ.command` は Python 3.12 を自動で探し
（無ければ Homebrew で導入）、.venv を 3.12 で作り直す（旧 .venv は退避）。
```
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu   # Macは通常の pip install torch でMPS版
.venv/bin/pip install diffusers==0.30.3 transformers==4.46.3 accelerate
```
※ transformers v5 は AudioLDM2 が使う GPT2 の生成APIを削除していて動かない。
必ず上記の版数で固定すること（`requirements.txt` にも明記）。

## 検証結果（このVM）
- 簡易シンセ5種の生成（波形・ピーク・RMS）を確認
- API: engines / library / generate / file ダウンロード（192KB WAV）すべて 200
- カタログの pronama mp3 URL が実際に引けることを確認（200）
