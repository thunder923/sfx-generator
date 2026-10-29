# 効果音ジェネレーター — SFX Generator

無料AIで効果音を作る＋フリー音源から選べる、Webアプリ（Macでは .command で起動）。

## 保持仕様（実装済み）
- **お気に入りだけ保持**: お気に入りはブラウザ側に保存（生成音は IndexedDB、ライブラリ音源は localStorage）→ **サイトを閉じても残る**
- **それ以外は消える**: 生成結果はサーバーのメモリ(RAM)と画面上だけに存在 → リロード／サーバー再起動で消える。サーバーはディスクに何も書かない
- **ローカルにダウンロード可**: 全アイテムに ⬇ DL ボタン

## 2つの生成エンジン
| エンジン | 内容 | 状態 |
|---|---|---|
| AI（AudioLDM2） | 無料・ローカル・APIキー不要の text-to-audio モデル（cvssp/audioldm2、diffusers）。日本語プリセットは英語プロンプトに自動変換して生成する。初回はモデル約3.5GBを自動DL。CPUだと10秒生成に数分、Mac(Apple Silicon MPS)／GPU推奨 | ✅ 実生成まで検証済み（2026-10-27）: 「爆発」5秒を生成成功（RMS 0.114 / peak 0.744）。このVMのCPUでは生成約5分。サンプル: `sample_audioldm2_explosion.wav`。バージョン固定が必須（下記） |
| 簡易シンセ（手続き型） | DSP合成レシピ12種（爆発／雨／風／雷／波／ビープ／チャイム／ノック／足音／水滴／剣／魔法）。AIモデル不要で即時生成。AIエンジンが使えない環境ではこちらがフォールバックになる | ✅ 動作検証済み |

## フリー音源ライブラリ
- 出典: [プロ生 無料素材 (sounds.pronama.jp)](https://sounds.pronama.jp/)
- プロ生無料素材（ゲームBGM）21件を、実在確認した直接mp3 URLでカタログ化（`data/library.json` の items。試聴／DL／お気に入り可）
- カテゴリーで利用条件が違うので、使う前に必ず元サイトで条件確認（アプリ内にも明記＋リンク）
- 効果音カテゴリー（HSP3／Adobe Audition 等）は元サイトへのリンク（`data/library.json` の browse_links）から辿れる。カタログ追加は `data/library.json` に行を足すだけ

## 起動方法（Mac）
1. **初回だけ（AI生成も使う場合）**: `mac/AIセットアップ.command` をダブルクリック
   （.venv 作成＋基本ライブラリ＋PyTorch＋AudioLDM2 用の diffusers 等を一括導入）
   - 簡易シンセとライブラリだけなら、この手順なしでも起動できる（.venv は起動時に自動作成される）
2. **通常起動**: `mac/一発起動.command` をダブルクリック → Safari で http://localhost:8300 が開く
   - 既に起動中ならブラウザを開くだけ（多重起動しない）
   - サーバー直起動: `.venv/bin/python app.py`（ポート 8300）
3. 終了: バックグラウンドで動き続けるので、止めたいときはアクティビティモニタ等で python プロセスを終了する。ログは `sfx.log`

## 使い方
1. プリセット（爆発・雨など）を選ぶか、作りたい音を入力して生成
   - AIエンジンがある場合はAI生成、無い場合は簡易シンセで即時生成される
2. 試聴して、気に入ったら ♡ お気に入り（ブラウザに残る）／ ⬇ DL（ファイルとして保存）
3. ライブラリタブではフリー音源を試聴・DL・お気に入りできる（利用条件は元サイトで確認）

## AIエンジンの入れ方（Mac想定・VMで検証済みの組み合わせ）
```
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu   # Macは通常の pip install torch でMPS版
.venv/bin/pip install diffusers==0.30.3 transformers==4.46.3 accelerate
```
※ transformers v5 は AudioLDM2 が使う GPT2 の生成APIを削除していて動かない。
必ず上記の版数で固定すること（`requirements.txt` にも明記）。Mac では `mac/AIセットアップ.command` が同じ内容を一括実行する。

## 検証結果（このVM・2026-10-27）
- 簡易シンセ5種の生成（波形・ピーク・RMS）を確認
- API: engines / library / generate / file ダウンロード（192KB WAV）すべて 200
- カタログの pronama mp3 URL が実際に引けることを確認（200）
