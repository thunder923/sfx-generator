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
]


def preset_for(prompt: str) -> dict | None:
    for p in PRESETS:
        if prompt.strip() == p["jp"]:
            return p
    return None
