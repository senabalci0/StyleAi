from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import random

app = Flask(__name__)
CORS(app)
BASE_DIR = Path(__file__).resolve().parent

STYLE_DB = {
    "daily": {
        "items": ["T-shirt", "Jeans", "Sneakers", "Light jacket", "Cap"],
        "warm": ["T-shirt", "Shorts", "Sneakers", "Sunglasses"],
        "cold": ["Sweater", "Jeans", "Coat", "Boots"],
    },
    "sport": {
        "items": ["Hoodie", "Joggers", "Running shoes", "Sport T-shirt"],
        "warm": ["Tank top", "Shorts", "Running shoes"],
        "cold": ["Hoodie", "Joggers", "Windbreaker", "Sneakers"],
    },
    "smart": {
        "items": ["Shirt", "Blazer", "Chinos", "Loafers"],
        "warm": ["Light shirt", "Chinos", "Loafers"],
        "cold": ["Shirt", "Blazer", "Coat", "Formal shoes"],
    },
    "wedding": {
        "items": ["Suit", "Dress shoes", "Watch", "Tie", "Dress"],
        "warm": ["Light suit", "Dress shoes", "Minimal accessories"],
        "cold": ["Suit", "Coat", "Elegant shoes"],
    },
}


def get_weather_category(temp, rain):
    if rain > 60:
        return "rainy"
    if temp <= 12:
        return "cold"
    elif temp <= 24:
        return "normal"
    else:
        return "warm"


def generate_outfit(style, weather):
    temp = weather.get("temp", 20)
    rain = weather.get("precip", 0)
    category = get_weather_category(temp, rain)

    style_data = STYLE_DB.get(style, STYLE_DB["daily"])

    if category == "cold":
        base_items = style_data.get("cold", style_data["items"])
    elif category == "warm":
        base_items = style_data.get("warm", style_data["items"])
    else:
        base_items = style_data["items"]

    items = random.sample(base_items, min(3, len(base_items)))
    return items


@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    style = data.get("style", "daily")
    weather = data.get("weather", {"temp": 20, "precip": 0})

    items = generate_outfit(style, weather)

    response = {
        "title": f"{style.capitalize()} AI Outfit",
        "style": style,
        "weather_context": weather,
        "items": items,
        "tip": "Generated based on style + weather + smart rules",
        "confidence": "high",
    }
    return jsonify(response)


@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    allowed_files = {"app.js", "style.css", "index.html"}
    if filename in allowed_files:
        return send_from_directory(BASE_DIR, filename)
    return ("Not Found", 404)


if __name__ == "__main__":
    app.run(debug=True)