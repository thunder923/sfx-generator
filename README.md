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
- 出典: [プロ生 無料素材 (sounds.pronama.jp)](https://sounds.pronama.jp/)
- プロ生 無料素材（ゲームBGM）21件を、実在確認した直接mp3 URLでカタログ化（試聴／DL／お気に入り可）
- カテゴリーで利用条件が違うので、使う前に必ず元サイトで条件確認（アプリ内にも明記＋リンク）
- 効果音カテゴリー（HSP3／Adobe Audition 等）は元サイトへのリンクから辿れる。カタログ追加は `data/library.json` に行を足すだけ

## 起動
```
.venv/bin/python app.py        # http://localhost:8300
# Mac: mac/一発起動.command（Safariで開く）
```

## AIエンジンの入れ方（Mac想定・VMで検証済みの組み合わせ）
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
