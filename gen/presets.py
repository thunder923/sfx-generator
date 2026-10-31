"""Japanese preset prompts -> English AudioLDM2 prompts (+ procedural recipe)."""

PRESETS = [
    {"jp": "爆発", "en": "A large explosion with deep rumble and debris", "recipe": "explosion"},
    {"jp": "雨", "en": "Heavy rain falling on a roof, natural ambience", "recipe": "rain"},
    {"jp": "風", "en": "Strong wind howling through trees", "recipe": "wind"},
    {"jp": "雷", "en": "A loud thunder strike with rolling rumble", "recipe": "thunder"},
    {"jp": "波・海", "en": "Ocean waves crashing on a beach", "recipe": "waves"},
    {"jp": "電子音・決定音", "en": "Retro video game UI beep sound, clean and short", "recipe": "beep"},
    {"jp": "チャイム", "en": "A gentle doorbell chime, two tones", "recipe": "chime"},
    {"jp": "ドアをノック", "en": "Knocking on a wooden door twice", "recipe": "knock"},
    {"jp": "足音", "en": "Footsteps walking on gravel", "recipe": "footsteps"},
    {"jp": "水滴", "en": "Water droplets dripping into a puddle", "recipe": "droplet"},
    {"jp": "剣の斬撃", "en": "A sword slash whoosh with metallic ring", "recipe": "sword"},
    {"jp": "魔法・キラキラ", "en": "Magical sparkling chimes, fantasy spell sound", "recipe": "magic"},
    {"jp": "鳥のさえずり", "en": "Birds chirping in a morning forest", "recipe": None},
    {"jp": "車のエンジン", "en": "A car engine starting and idling", "recipe": None},
    {"jp": "銃声", "en": "A single gunshot with echo", "recipe": None},
    {"jp": "ガラスの割れる音", "en": "Glass shattering on a hard floor", "recipe": None},
    {"jp": "猫の鳴き声", "en": "A cat meowing close to the microphone", "recipe": None},
    {"jp": "拍手", "en": "Audience applause in a concert hall", "recipe": None},
    {"jp": "川のせせらぎ", "en": "A gentle river stream flowing over rocks, babbling water ambience, no music", "recipe": None},
    {"jp": "滝", "en": "A waterfall, powerful rushing water ambience", "recipe": None},
    {"jp": "焚き火", "en": "A campfire crackling, wood fire ambience", "recipe": None},
    {"jp": "雨の日の室内", "en": "Rain sounds heard from indoors, rain on window glass", "recipe": None},
]


def preset_for(prompt: str) -> dict | None:
    for p in PRESETS:
        if prompt.strip() == p["jp"]:
            return p
    return None


# Free-form Japanese input: AudioLDM2 only understands English, so raw
# Japanese prompts condition the model on noise and yield weird sounds.
# Map common SFX keywords to English phrases; returns None when nothing
# matches (caller then passes the text through, e.g. English input).
_KEYWORDS = [
    ("川のせせらぎ", "a gentle river stream flowing over rocks, babbling water"),
    ("せせらぎ", "a small stream, babbling water"),
    ("小川", "a small stream flowing, gentle water"),
    ("川", "a river stream flowing, water ambience"),
    ("滝", "a waterfall, rushing water"),
    ("海", "ocean waves on a beach"),
    ("波", "waves lapping"),
    ("雨", "rain falling"),
    ("風", "wind blowing"),
    ("雷", "thunder rumbling"),
    ("爆発", "a large explosion"),
    ("鳥", "birds chirping"),
    ("猫", "a cat meowing"),
    ("犬", "a dog barking"),
    ("銃", "a gunshot"),
    ("ガラス", "glass shattering"),
    ("剣", "a sword slash whoosh"),
    ("魔法", "magical sparkling chimes"),
    ("足音", "footsteps"),
    ("水滴", "water droplets dripping"),
    ("チャイム", "a doorbell chime"),
    ("ノック", "knocking on a door"),
    ("エンジン", "a car engine"),
    ("拍手", "applause"),
    ("焚き火", "a campfire crackling"),
    ("火", "fire crackling"),
    ("電車", "a train passing"),
    ("車", "a car passing by"),
    ("ドア", "a door opening and closing"),
    ("鐘", "a bell ringing"),
    ("ピアノ", "a piano playing"),
    ("笑い声", "people laughing"),
    ("悲鳴", "a scream"),
]


def translate_free(prompt: str) -> str | None:
    text = prompt.strip()
    if not text or all(ord(c) < 128 for c in text):
        return None  # empty or already English/ASCII: pass through as-is
    hits = [en for jp, en in _KEYWORDS if jp in text]
    if not hits:
        return None
    seen: list[str] = []
    for h in hits:
        if h not in seen:
            seen.append(h)
    return ", ".join(seen[:3]) + ", natural sound effect, no music, no speech"
