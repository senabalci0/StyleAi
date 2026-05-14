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

STYLE_COPY = {
    "daily": {
        "label": "Casual",
        "base": [
            "Plain T-shirt or light knit",
            "Relaxed jeans or chinos",
            "Clean sneakers",
            "Minimal watch or small accessory",
        ],
        "mood": "easy, polished, and comfortable all day",
    },
    "sport": {
        "label": "Sport",
        "base": ["Breathable top", "Joggers or leggings", "Supportive sneakers", "Light zip layer"],
        "mood": "active, light, and easy to move in",
    },
    "smart": {
        "label": "Smart",
        "base": [
            "Shirt, blouse, or fine turtleneck",
            "Tailored trousers or midi skirt",
            "Loafers, boots, or refined sneakers",
            "Clean-lined jacket",
        ],
        "mood": "intentional, simple, and city-ready",
    },
    "wedding": {
        "label": "Wedding",
        "base": ["Dress or suit", "Elegant shoes", "Subtle jewelry", "Photo-friendly finishing layer"],
        "mood": "celebratory, elegant, and balanced",
    },
}

WEATHER_CODES = {
    0: "Clear",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Cloudy",
    45: "Foggy",
    48: "Foggy",
    51: "Drizzle",
    53: "Drizzle",
    55: "Drizzle",
    61: "Rainy",
    63: "Rainy",
    65: "Heavy rain",
    71: "Snowy",
    73: "Snowy",
    75: "Heavy snow",
    80: "Showers",
    81: "Showers",
    82: "Heavy showers",
    95: "Stormy",
}


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


def pick_closet_items(style: str, weather: dict, closet: list[dict]) -> list[dict]:
    def pick(category: str) -> dict | None:
        matches = [item for item in closet if item.get("category") == category]
        return random.choice(matches) if matches else None

    picks: list[dict | None] = []
    if style == "wedding":
        picks.append(pick("dress") or pick("top"))
    else:
        picks.extend([pick("top"), pick("bottom")])

    if float(weather.get("temp", 18)) <= 18 or float(weather.get("wind", 12)) >= 20 or float(weather.get("precip", 20)) >= 45:
        picks.append(pick("outerwear"))

    picks.extend([pick("shoes"), pick("accessory")])
    return [item for item in picks if item]


def build_recommendation(payload: dict) -> dict:
    style = payload.get("style", "daily")
    selected_style = STYLE_COPY.get(style, STYLE_COPY["daily"])
    weather = payload.get("weather") or {"temp": 18, "wind": 12, "precip": 20, "code": 2}
    prefs = payload.get("prefs") or {}
    closet = payload.get("closet") or []
    closet_pieces = pick_closet_items(style, weather, closet)
    closet_names = [
        f"{CATEGORY_LABELS.get(item.get('category'), 'Item')}: {item.get('name', 'Closet item')}"
        for item in closet_pieces
    ]
    code = int(weather.get("code", 2) or 2)
    temp = round(float(weather.get("temp", 18)))

    if payload.get("hasPhoto") and prefs.get("photoAware", True):
        note = "Python used the uploaded photo as the anchor piece, then balanced the outfit around it."
    elif closet_pieces:
        note = "Python selected these pieces from your saved closet."
    else:
        note = "Python could not find matching closet pieces, so it used general wardrobe suggestions."

    return {
        "id": f"py-{int(datetime.now().timestamp() * 1000)}",
        "title": f"{selected_style['label']} outfit",
        "meta": f"{payload.get('dayText', 'Selected day')} {payload.get('startTime', '08:00')}-{payload.get('endTime', '10:00')}",
        "summary": f"{temp}C and {WEATHER_CODES.get(code, 'variable').lower()} weather: {selected_style['mood']}.",
        "items": closet_names or selected_style["base"] + weather_advice(weather, prefs),
        "note": note,
        "image": (closet_pieces[0].get("image") if closet_pieces else "") or payload.get("photo", ""),
        "closetPieces": closet_pieces,
        "tags": [selected_style["label"], f"{temp}C", "Python engine", "From closet" if closet_pieces else "General idea"],
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