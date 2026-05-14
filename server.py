from __future__ import annotations

import json
import mimetypes
import random
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 5173

CATEGORY_LABELS = {
    "top": "Top",
    "bottom": "Bottom",
    "outerwear": "Outerwear",
    "shoes": "Shoes",
    "accessory": "Accessory",
    "dress": "Dress / suit",
}

STYLE_CONFIG = {
    "daily": {
        "label": "Casual",
        "formality": 0,
        "preferred_categories": ["top", "bottom", "shoes", "accessory"],
        "avoid_categories": ["dress"],
        "blocked_keywords": ["suit", "blazer", "tuxedo", "gown", "heels", "tie", "bow tie"],
        "required_categories": {"top": "a top", "bottom": "bottoms", "shoes": "shoes"},
        "base": [
            "Plain T-shirt or light knit",
            "Relaxed jeans or chinos",
            "Clean sneakers",
            "Minimal watch or small accessory",
        ],
        "mood": "easy, polished, and comfortable all day",
        "color_palettes": ["neutrals", "earth", "pastel"],
    },
    "sport": {
        "label": "Sport",
        "formality": 0,
        "preferred_categories": ["top", "bottom", "shoes"],
        "avoid_categories": ["dress", "accessory"],
        "blocked_keywords": [
            "suit", "blazer", "tuxedo", "gown", "heels", "tie", "bow tie",
            "dress shirt", "loafer", "oxford", "jeans", "chinos", "trousers",
        ],
        "required_categories": {"top": "a sport top", "bottom": "sport bottoms", "shoes": "sport shoes"},
        "base": ["Breathable top", "Joggers or leggings", "Supportive sneakers", "Light zip layer"],
        "mood": "active, light, and easy to move in",
        "color_palettes": ["bold", "monochrome"],
    },
    "smart": {
        "label": "Smart",
        "formality": 2,
        "preferred_categories": ["top", "bottom", "outerwear", "shoes", "accessory"],
        "avoid_categories": [],
        "blocked_keywords": [
            "t-shirt", "tshirt", "hoodie", "sweatshirt", "jogger", "legging",
            "shorts", "flip flop", "crocs", "tracksuit", "eşofman",
        ],
        "required_categories": {"top": "a smart top (shirt/blouse)", "bottom": "smart bottoms (trousers/skirt)", "shoes": "smart shoes"},
        "base": [
            "Shirt, blouse, or fine turtleneck",
            "Tailored trousers or midi skirt",
            "Loafers, boots, or refined sneakers",
            "Clean-lined jacket",
        ],
        "mood": "intentional, simple, and city-ready",
        "color_palettes": ["neutrals", "monochrome", "earth"],
    },
    "wedding": {
        "label": "Wedding",
        "formality": 3,
        "preferred_categories": ["dress", "shoes", "accessory"],
        "avoid_categories": ["top", "bottom"],
        "blocked_keywords": [
            "t-shirt", "tshirt", "hoodie", "sweatshirt", "jogger", "legging",
            "shorts", "sneaker", "flip flop", "crocs", "tracksuit", "eşofman",
            "jeans", "chinos", "cargo", "parka", "puffer",
        ],
        "required_categories": {"dress": "a dress or suit (add one under 'Dress / suit' category)"},
        "base": ["Dress or suit", "Elegant shoes", "Subtle jewelry", "Photo-friendly finishing layer"],
        "mood": "celebratory, elegant, and balanced",
        "color_palettes": ["pastel", "neutrals", "jewel"],
    },
}

WEATHER_CODES = {
    0: "Clear", 1: "Mostly clear", 2: "Partly cloudy", 3: "Cloudy",
    45: "Foggy", 48: "Foggy", 51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
    61: "Rainy", 63: "Rainy", 65: "Heavy rain",
    71: "Snowy", 73: "Snowy", 75: "Heavy snow",
    80: "Showers", 81: "Showers", 82: "Heavy showers",
    95: "Stormy",
}


COLOR_GROUPS: dict[str, str] = {
    "white": "neutral", "off-white": "neutral", "cream": "neutral", "beige": "neutral",
    "ivory": "neutral", "light gray": "neutral", "gray": "neutral", "grey": "neutral",
    "dark gray": "neutral", "charcoal": "neutral", "black": "neutral",
    "brown": "earth", "tan": "earth", "camel": "earth", "khaki": "earth",
    "olive": "earth", "dark green": "earth", "forest green": "earth",
    "rust": "earth", "terracotta": "earth", "mustard": "earth",
    "light blue": "pastel", "sky blue": "pastel", "baby blue": "pastel",
    "light pink": "pastel", "blush": "pastel", "lavender": "pastel",
    "mint": "pastel", "light yellow": "pastel", "peach": "pastel",
    "red": "bold", "bright red": "bold", "orange": "bold", "yellow": "bold",
    "green": "bold", "bright blue": "bold", "cobalt": "bold",
    "purple": "bold", "fuchsia": "bold", "hot pink": "bold",
    "navy": "jewel", "burgundy": "jewel", "wine": "jewel", "emerald": "jewel",
    "teal": "jewel", "deep purple": "jewel", "royal blue": "jewel",
    "dark brown": "jewel",
}

HARMONY_MAP: dict[str, list[str]] = {
    "neutral":   ["neutral", "earth", "pastel", "bold", "jewel"],  
    "earth":     ["earth", "neutral", "jewel"],
    "pastel":    ["pastel", "neutral"],
    "bold":      ["bold", "neutral"],
    "jewel":     ["jewel", "neutral", "earth"],
}


def detect_color_group(name: str) -> str | None:
    """Kıyafet adından renk grubu tahmin et (basit keyword eşleşmesi)."""
    name_lower = name.lower()
    for color_kw, group in COLOR_GROUPS.items():
        if color_kw in name_lower:
            return group
    return None


def color_harmony_score(pieces: list[dict]) -> tuple[int, str]:
    """
    Seçilen parçaların renk uyumunu puanla.
    Döner: (0-100 arası puan, açıklama metni)
    """
    groups = [detect_color_group(p.get("name", "")) for p in pieces]
    groups = [g for g in groups if g]

    if not groups:
        return 50, "Color info not found in item names — add color keywords (e.g. 'navy trousers') for better matching."

    base = groups[0]
    compatible = HARMONY_MAP.get(base, ["neutral"])
    matches = sum(1 for g in groups[1:] if g in compatible)
    total = max(len(groups) - 1, 1)
    score = round((matches / total) * 100)

    if score >= 80:
        note = f"Great color harmony — all pieces work well together ({base} palette)."
    elif score >= 50:
        note = f"Decent color mix — some pieces clash slightly. Try keeping extras in neutral tones."
    else:
        note = f"Color mismatch detected. The {base} palette doesn't mix well with all selected pieces."

    return score, note


def formality_score(item_name: str) -> int:
    """
    Kıyafet adından formality tahmini (0=çok casual, 3=çok formal).
    Basit keyword tabanlı.
    """
    name = item_name.lower()
    formal_kws = ["suit", "blazer", "dress shirt", "tie", "oxford", "loafer", "trousers", "skirt", "heels", "dress"]
    casual_kws = ["t-shirt", "tshirt", "jeans", "sneaker", "hoodie", "jogger", "legging", "sweatshirt", "shorts"]

    formal_hits = sum(1 for k in formal_kws if k in name)
    casual_hits = sum(1 for k in casual_kws if k in name)

    if formal_hits >= 2:
        return 3
    if formal_hits == 1:
        return 2
    if casual_hits >= 1:
        return 0
    return 1 


def weather_advice(weather: dict, prefs: dict) -> list[str]:
    temp = float(weather.get("temp", 18))
    precip = float(weather.get("precip", 20))
    wind = float(weather.get("wind", 12))
    pieces: list[str] = []

    if temp <= 7:
        pieces.extend(["heavy coat or wool overcoat", "scarf", "closed shoes"])
    if 7 < temp <= 15:
        pieces.extend(["mid-weight jacket", "long-sleeve top"])
    if 15 < temp <= 24:
        pieces.append("light jacket or shirt layer")
    if temp > 24:
        pieces.extend(["breathable lightweight fabric", "sunglasses"])
    if precip >= 45 and prefs.get("rainReady", True):
        pieces.extend(["water-resistant outer layer", "umbrella"])
    if wind >= 25:
        pieces.append("wind-stable layer")

    return pieces


def is_blocked(item_name: str, blocked_keywords: list[str]) -> bool:
    """Kıyafet adı herhangi bir blocked keyword içeriyor mu?"""
    name_lower = item_name.lower()
    return any(kw in name_lower for kw in blocked_keywords)


def pick_closet_items_for_style(style: str, weather: dict, closet: list[dict]) -> tuple[list[dict], list[str]]:
    """
    Stil ve hava durumuna göre closet'ten akıllıca parça seç.
    Döner: (seçilen parçalar, uyarı listesi)
    """
    config = STYLE_CONFIG.get(style, STYLE_CONFIG["daily"])
    target_formality = config["formality"]
    preferred = config["preferred_categories"]
    avoid = config["avoid_categories"]
    blocked_keywords = config.get("blocked_keywords", [])
    required_categories = config.get("required_categories", {})
    warnings: list[str] = []

   
    eligible = [
        item for item in closet
        if item.get("category") not in avoid
        and not is_blocked(item.get("name", ""), blocked_keywords)
    ]

    def candidates_for(category: str) -> list[dict]:
        items = [i for i in eligible if i.get("category") == category]
        items.sort(key=lambda i: abs(formality_score(i.get("name", "")) - target_formality))
        return items

    def pick(category: str) -> dict | None:
        pool = candidates_for(category)
        if not pool:
            return None
        top = pool[:3]
        return random.choice(top)

    picks: list[dict] = []

    if style == "wedding":
        item = pick("dress")
        if item:
            picks.append(item)
    else:
        top_item = pick("top")
        bottom_item = pick("bottom")
        if top_item:
            picks.append(top_item)
        if bottom_item:
            picks.append(bottom_item)

    temp = float(weather.get("temp", 18))
    wind = float(weather.get("wind", 12))
    precip = float(weather.get("precip", 20))
    if temp <= 18 or wind >= 20 or precip >= 45:
        outer = pick("outerwear")
        if outer:
            picks.append(outer)

    if "shoes" in preferred:
        shoes = pick("shoes")
        if shoes:
            picks.append(shoes)

    if "accessory" in preferred:
        acc = pick("accessory")
        if acc:
            picks.append(acc)

    picked_categories = {p.get("category") for p in picks}
    for cat, description in required_categories.items():
        if cat not in picked_categories:
            raw_in_closet = any(i.get("category") == cat for i in closet if i.get("category") not in avoid)
            blocked_in_closet = any(
                i.get("category") == cat and is_blocked(i.get("name", ""), blocked_keywords)
                for i in closet
            )
            if blocked_in_closet and not raw_in_closet:
                warnings.append(
                    f"⚠ The {cat} items in your closet are not suitable for a {config['label'].lower()} look. "
                    f"Please add {description} to your closet."
                )
            elif not raw_in_closet:
                warnings.append(
                    f"⚠ No {cat} found in your closet for this style. "
                    f"Please add {description} to your closet."
                )

    return picks, warnings


def build_recommendation(payload: dict) -> dict:
    style = payload.get("style", "daily")
    config = STYLE_CONFIG.get(style, STYLE_CONFIG["daily"])
    weather = payload.get("weather") or {"temp": 18, "wind": 12, "precip": 20, "code": 2}
    prefs = payload.get("prefs") or {}
    closet = payload.get("closet") or []

    closet_pieces, formality_warnings = pick_closet_items_for_style(style, weather, closet)

    closet_names = [
        f"{CATEGORY_LABELS.get(item.get('category'), 'Item')}: {item.get('name', 'Closet item')}"
        for item in closet_pieces
    ]

    harmony_score, harmony_note = color_harmony_score(closet_pieces)

    code = int(weather.get("code", 2) or 2)
    temp = round(float(weather.get("temp", 18)))

    if closet_names:
        items = closet_names + weather_advice(weather, prefs)
        source = "closet"
    else:
        items = config["base"] + weather_advice(weather, prefs)
        source = "general"

    
    if payload.get("hasPhoto") and prefs.get("photoAware", True):
        note = "The uploaded photo was used as the anchor piece — outfit was matched around its formality level."
    elif source == "closet":
        note = f"Pieces selected from your closet based on {config['label'].lower()} formality level."
    else:
        note = "No matching closet pieces found — using general wardrobe suggestions for this style."

    if formality_warnings:
        note += "\n" + "\n".join(formality_warnings)

    return {
        "id": f"py-{int(datetime.now().timestamp() * 1000)}",
        "title": f"{config['label']} outfit",
        "meta": f"{payload.get('dayText', 'Selected day')} {payload.get('startTime', '08:00')}-{payload.get('endTime', '10:00')}",
        "summary": f"{temp}°C and {WEATHER_CODES.get(code, 'variable').lower()} weather — {config['mood']}.",
        "items": items,
        "note": note,
        "image": (closet_pieces[0].get("image") if closet_pieces else "") or payload.get("photo", ""),
        "closetPieces": closet_pieces,
        "harmonyScore": harmony_score,
        "harmonyNote": harmony_note,
        "formalityTarget": config["formality"],
        "tags": [
            config["label"],
            f"{temp}°C",
            f"Harmony {harmony_score}%",
            "From closet" if source == "closet" else "General idea",
        ],
        "createdAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


class StyleAIHandler(BaseHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_GET(self) -> None:
        requested = unquote(self.path.split("?", 1)[0]).lstrip("/") or "index.html"
        path = (ROOT / requested).resolve()

        if not str(path).startswith(str(ROOT)) or not path.is_file():
            self.send_error(404, "File not found")
            return

        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:
        if self.path != "/api/recommend":
            self.send_error(404, "Unknown API endpoint")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            response = json.dumps(build_recommendation(payload)).encode("utf-8")
        except Exception as error:
            self.send_response(400)
            response = json.dumps({"error": str(error)}).encode("utf-8")
        else:
            self.send_response(200)

        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args: object) -> None:
        print(f"[StyleAI] {self.address_string()} - {format % args}")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), StyleAIHandler)
    print(f"StyleAI Python server running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()