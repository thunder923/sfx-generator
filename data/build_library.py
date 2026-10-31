#!/usr/bin/env python3
"""Rebuild data/library.json adding HSP3 (full catalog), Adobe Audition and
VSQ plus+ as sources/browse links. Idempotent: drops previously added
hsp3-* items and regenerates the whole file from the pronama BGM base."""
import json
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent / "data" / "library.json"
data = json.loads(LIB.read_text(encoding="utf-8"))

# keep only the original pronama BGM items as the base
items = [i for i in data["items"] if not i["id"].startswith("hsp3-")]
for i in items:
    i.setdefault("source", "プロ生 無料素材")

HSP3_SOUNDS_PAGE = "https://sounds.pronama.jp/hsp3/sounds/"
HSP3_BGM_PAGE = "https://sounds.pronama.jp/hsp3/bgm/"
A = "https://audio.sounds.pronama.jp/hsp3/sounds/"
B = "https://audio.sounds.pronama.jp/hsp3/bgm/"

# (file, title, extra tags) — titles as shown on sounds.pronama.jp/hsp3/sounds/ (34)
sounds = [
    ("explos", "爆発 (explos)", ["爆発"]),
    ("inject", "注入", []),
    ("jp_dead", "死亡", []),
    ("jp_jump", "ジャンプ (jp_jump)", ["ジャンプ"]),
    ("se01", "SE01", []), ("se02", "SE02", []), ("se03", "SE03", []),
    ("se04", "SE04", []), ("se05", "SE05", []), ("se06", "SE06", []),
    ("se07", "SE07", []), ("se08", "SE08", []), ("se09", "SE09", []),
    ("se10", "SE10", []), ("se11", "SE11", []), ("se12", "SE12", []),
    ("se13", "SE13", []), ("se14", "SE14", []), ("se15", "SE15", []),
    ("se_aaa", "SE (se_aaa)", []),
    ("se_block2", "ブロック、バリア", ["バリア"]),
    ("se_bom", "爆発 (se_bom)", ["爆発"]),
    ("se_break", "破壊 (se_break)", ["破壊"]),
    ("se_break2", "破壊 (se_break2)", ["破壊"]),
    ("se_break3", "破壊 (se_break3)", ["破壊"]),
    ("se_click", "クリック", ["クリック"]),
    ("se_foot", "足音", ["足音"]),
    ("se_jump", "ジャンプ (se_jump)", ["ジャンプ"]),
    ("se_jump2", "ジャンプ (se_jump2)", ["ジャンプ"]),
    ("se_puyo", "ぷよ", []),
    ("se_shot", "ショット (se_shot)", ["ショット"]),
    ("se_shot2", "ショット (se_shot2)", ["ショット"]),
    ("se_tyuiin", "ちゅいん", []),
    ("sel", "選択", ["選択"]),
]
for fname, title, extra in sounds:
    items.append({
        "id": f"hsp3-se-{fname}",
        "title": title,
        "mp3": f"{A}{fname}.mp3",
        "page": HSP3_SOUNDS_PAGE,
        "tags": ["HSP3", "効果音", "ゲーム"] + extra,
        "source": "HSP3 無料素材",
    })

# (file, title) — as shown on sounds.pronama.jp/hsp3/bgm/ (18)
bgms = [
    ("bgm2", "BGM2: コルタ村ふたり"),
    ("bgm04", "BGM4: Inline Trap"),
    ("bgm5", "BGM5: Hello my Senegal animals"),
    ("bgm06", "BGM6: Jumpper 3 theme"),
    ("bgm7", "BGM7: smart and active"),
    ("bgm8", "BGM8: 潮が満ちる"),
    ("bgm9", "BGM9: トンネルの森"),
    ("bgm10", "BGM10: どりっぷまーち"),
    ("bgm11", "BGM11: どりっぷまーち2"),
    ("bgm12", "BGM12: Quartermind"),
    ("bgm13", "BGM13: Wired trouble"),
    ("bgm14", "BGM14: Breeze time"),
    ("bgm15", "BGM15: march of elements"),
    ("bgm16", "BGM16: Beyond the fire"),
    ("bgm17", "BGM17: Vector"),
    ("bgm18", "BGM18: floating power"),
    ("bgm19", "BGM19: travernt"),
    ("bgm20", "BGM20: Invisible Idol of Rome"),
]
for fname, title in bgms:
    items.append({
        "id": f"hsp3-bgm-{fname}",
        "title": title,
        "mp3": f"{B}{fname}.mp3",
        "page": HSP3_BGM_PAGE,
        "tags": ["HSP3", "BGM", "ゲーム"],
        "source": "HSP3 無料素材",
    })

AUD = "https://sounds.pronama.jp/audition"
audition_links = [
    ("アンビエンス（屋内・施設）", f"{AUD}/ambience1/"),
    ("アンビエンス（屋外・自然）", f"{AUD}/ambience2/"),
    ("動物の鳴き声（179件）", f"{AUD}/animals/"),
    ("カートゥーン効果音", f"{AUD}/cartoon/"),
    ("クラッシュ・破壊音", f"{AUD}/crashes/"),
    ("ドローン・持続低音", f"{AUD}/drones/"),
    ("緊急事態・サイレン", f"{AUD}/emergencyeffects/"),
    ("炎と爆発", f"{AUD}/fireandexplosions/"),
    ("フォーリー（生活音・物音）", f"{AUD}/foley/"),
    ("フォーリー（足音）", f"{AUD}/foleyfootsteps/"),
    ("家庭・日用品（606件）", f"{AUD}/household/"),
    ("ホラー効果音", f"{AUD}/horror/"),
    ("人の声・体の音", f"{AUD}/humanelements/"),
    ("イメージング素材", f"{AUD}/imagingelements/"),
    ("インパクト・打撃音", f"{AUD}/impacts/"),
    ("工業・機械音", f"{AUD}/industry/"),
    ("液体・水音", f"{AUD}/liquidandwater/"),
    ("Web・UI・マルチメディア", f"{AUD}/multimedia/"),
    ("ノイズ・トーン・DTMF・テスト", f"{AUD}/noisetonesdtmfandtests/"),
    ("プロダクション・エレメント", f"{AUD}/productionelements/"),
    ("SF・サイエンスフィクション", f"{AUD}/sciencefiction/"),
    ("スポーツ効果音", f"{AUD}/sports/"),
    ("テクノロジー・電子機器", f"{AUD}/technology/"),
    ("乗り物・交通機関", f"{AUD}/transportation/"),
    ("水中音（112件）", f"{AUD}/underwater/"),
    ("武器・銃声", f"{AUD}/weapons/"),
    ("気象・天気", f"{AUD}/weather/"),
]
VSQ = "https://vsq.co.jp/plus/sound/category"
vsq_links = [
    ("環境音", f"{VSQ}/environment/"),
    ("音楽/BGM", f"{VSQ}/music/"),
    ("テロップ/アニメ/CG", f"{VSQ}/sfx/"),
    ("人", f"{VSQ}/people/"),
    ("生活・いろいろ", f"{VSQ}/lifestyle/"),
    ("時代劇/日本", f"{VSQ}/samurai_japan/"),
    ("食べ物", f"{VSQ}/food/"),
    ("交通", f"{VSQ}/traffic/"),
    ("福岡の音", f"{VSQ}/fukuoka/"),
]

browse_links = [
    {"title": "プロ生 無料素材トップ（効果音・音声・BGM 全カテゴリー）", "url": "https://sounds.pronama.jp/", "group": "プロ生 無料素材"},
    {"title": "ゲームBGM カテゴリー", "url": "https://sounds.pronama.jp/pronama/bgm/", "group": "プロ生 無料素材"},
    {"title": "レトロ機器 カテゴリー", "url": "https://sounds.pronama.jp/pronama/retro/", "group": "プロ生 無料素材"},
    {"title": "プロ生 無料素材 案内・利用規約", "url": "https://sounds.pronama.jp/pronama/terms/", "group": "プロ生 無料素材"},
    {"title": "HSP3 効果音（34件・このライブラリに収録済み）", "url": HSP3_SOUNDS_PAGE, "group": "HSP3 無料素材"},
    {"title": "HSP3 BGM（18件・このライブラリに収録済み）", "url": HSP3_BGM_PAGE, "group": "HSP3 無料素材"},
    {"title": "HSP3 案内・利用規約", "url": "https://sounds.pronama.jp/hsp3/terms/", "group": "HSP3 無料素材"},
] + [
    {"title": f"Adobe Audition: {t}", "url": u, "group": "Adobe Audition"} for t, u in audition_links
] + [
    {"title": "Adobe Audition 案内・利用規約", "url": f"{AUD}/terms/", "group": "Adobe Audition"},
] + [
    {"title": "VSQ plus+ トップ（全1,726種類）", "url": "https://vsq.co.jp/plus/", "group": "VSQ plus+"},
] + [
    {"title": f"VSQ plus+: {t}", "url": u, "group": "VSQ plus+"} for t, u in vsq_links
] + [
    {"title": "VSQ plus+ ご利用規約", "url": "https://vsq.co.jp/plus/tos/", "group": "VSQ plus+"},
]

out = {
    "sources": [
        {"name": "プロ生 無料素材", "top_url": "https://sounds.pronama.jp/",
         "note": "カテゴリーによって利用条件が異なります。使う前に必ず元サイトで条件を確認してください。ゲームBGM 21件を収録。"},
        {"name": "HSP3 無料素材", "top_url": HSP3_SOUNDS_PAGE,
         "note": "プログラミング言語 HSP3 で提供されている効果音・BGM素材を、プロ生が許諾を得て転載しているもの。効果音34件＋BGM 18件を全件収録。ソフト作成時の使用・改変・配布が自由で著作権表記も不要、商用も一部を除き制限なし（素材そのものの販売は著作者へ要連絡）。"},
        {"name": "Adobe Audition Sound Effects", "top_url": "https://sounds.pronama.jp/audition/household/",
         "note": "ロイヤリティーフリー効果音（プロ生が日本語キーワード付きで一覧化）。件数が膨大なため、このライブラリからはカテゴリー別リンクで開く形にしています（元サイトで試聴・DL可、利用条件は元サイトで確認）。"},
        {"name": "VSQ plus+", "top_url": "https://vsq.co.jp/plus/",
         "note": "商用利用可能で1,726種類、クレジット表記不要・申請不要。ただし素材そのものの再配布・販売・貸与は禁止（利用規約）。このライブラリからはカテゴリー別リンクで開く形にしています。"},
    ],
    # backward-compat single-source field (old frontend used lib.source)
    "source": {"name": "プロ生 無料素材 ほか", "top_url": "https://sounds.pronama.jp/",
               "note": "出典ごとに利用条件が異なります。使う前に必ず各元のサイトで条件を確認してください。"},
    "browse_links": browse_links,
    "items": items,
}
LIB.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"items: {len(items)} (pronama {sum(1 for i in items if i['source']=='プロ生 無料素材')}, hsp3 {sum(1 for i in items if i['source']=='HSP3 無料素材')})")
print(f"browse_links: {len(browse_links)}")
