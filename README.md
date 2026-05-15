# StyleAI

A weather-aware outfit recommendation web app. StyleAI suggests outfits based on real-time weather, time of day, your personal style preference, and the clothes saved in your digital closet.

---

## Project Structure

```
StyleAI/
├── index.html       # UI structure
├── app.js           # Client-side application logic
├── styles.css       # Styling
└── server.py        # Python HTTP server + recommendation engine
```

---

## How to Run

1. Make sure Python 3.10 or higher is installed.
2. Open a terminal in the project folder.
3. Run the server:

```bash
python server.py
```

4. Open your browser and go to:

```
http://127.0.0.1:5173
```

> Do not open `index.html` directly in the browser — it must be served through the Python server for the outfit API to work.

---

## Features

### My Closet
Upload or capture a photo of a clothing item, give it a name and category, and save it to your closet. The recommendation engine picks from your closet when generating outfits. Up to 60 items can be stored. All closet data is saved in the browser's localStorage.

**Categories:**
- Top
- Bottom
- Outerwear
- Shoes
- Accessory
- Dress / suit

**Tip:** Include color words in the item name (e.g. "navy trousers", "white shirt") to enable color harmony analysis.

---

### Style Selection
Choose the occasion for your outfit:

| Style | Formality | Best for |
|---|---|---|
| Casual | 0 | Everyday, relaxed outings |
| Sport | 0 | Workouts, active use |
| Smart | 2 | Work, meetings, city errands |
| Wedding | 3 | Formal events, celebrations |

Each style has its own rules. Casual will never suggest a blazer or suit. Wedding will never suggest jeans, hoodies, or sneakers. If your closet doesn't have a suitable item for the selected style, a warning is shown telling you exactly what to add.

---

### Style-Based Filtering

Every closet item is evaluated against the selected style using two mechanisms:

**Blocked keywords** — Items whose names contain certain words are excluded entirely from that style. For example:
- `eşofman`, `hoodie`, `jogger` are blocked in Smart and Wedding
- `blazer`, `suit`, `heels` are blocked in Casual and Sport
- `jeans`, `sneaker`, `puffer` are blocked in Wedding

**Formality score** — Each item gets a score from 0 (very casual) to 3 (very formal) based on its name. Items closest to the target formality for the selected style are ranked first. The engine picks randomly from the top 3 matches to add variety.

---

### Priorities
Three optional toggles that adjust the recommendation:

- **Comfort** — Signals a comfort-first preference (used in outfit note).
- **Rain ready** — If rain probability is 45% or higher, adds a water-resistant layer and umbrella to the suggestion.
- **Use photo context** — If a photo is uploaded, it is used as the anchor piece and the outfit note reflects this.

---

### Weather Integration
Weather is fetched automatically from [Open-Meteo](https://open-meteo.com/) using the browser's geolocation. If location access is denied, Istanbul weather is used as a fallback. Weather updates when you change the day or start time.

Weather influences the outfit in two ways:
- The weather strip shows temperature, wind speed, and rain probability.
- The recommendation engine adds or removes layers based on these values (e.g. heavy coat under 7°C, umbrella above 45% rain).

---

### Color Harmony Score
When closet pieces are selected, their names are scanned for color keywords. Each color is assigned to a palette group (neutral, earth, pastel, bold, jewel). The engine checks whether the selected pieces' palettes are compatible and returns a score from 0 to 100.

| Score | Meaning |
|---|---|
| 80–100 | Great harmony |
| 50–79 | Decent mix, some clashing possible |
| 0–49 | Mismatch detected |

The score and a plain-language note are shown below the outfit list as a progress bar.

---

### Saving Outfits
After an outfit is generated:
- **I like it, save** — Saves the outfit to localStorage. Up to 12 outfits are kept.
- **Not for me** — Clears the card without saving.

Saved outfits appear in the Saved Outfits panel on the right with their photo, title, date, and time range.

---

## How the Recommendation Engine Works

When you click **Suggest outfit**, the following happens:

1. The app fetches current weather for your location and the selected time slot.
2. A `POST /api/recommend` request is sent to the Python server with your style, preferences, weather data, and closet contents.
3. The Python server filters the closet by `avoid_categories` and `blocked_keywords`, ranks remaining items by formality match, picks up to 3 candidates per category, and selects randomly among them for variety.
4. It also calculates the color harmony score and checks for missing required categories.
5. The server returns a complete outfit object with items, tags, harmony score, and any warnings.
6. If the Python server is unreachable, the JavaScript engine runs the same logic locally as a fallback — the output is identical in structure.

---

## Recommendation Rules per Style

### Casual
- Picks from: top, bottom, shoes, accessory
- Skips: dress / suit category
- Blocks: suit, blazer, tuxedo, gown, heels, tie, bow tie
- Required: top, bottoms, shoes

### Sport
- Picks from: top, bottom, shoes
- Skips: dress, accessory
- Blocks: suit, blazer, heels, dress shirt, loafer, oxford, jeans, chinos, trousers
- Required: sport top, sport bottoms, sport shoes

### Smart
- Picks from: top, bottom, outerwear, shoes, accessory
- Blocks: t-shirt, hoodie, sweatshirt, jogger, legging, shorts, flip flop, crocs, tracksuit, eşofman
- Required: smart top, smart bottoms, smart shoes

### Wedding
- Picks from: dress (Dress / suit category), shoes, accessory
- Skips: top, bottom categories entirely
- Blocks: t-shirt, hoodie, jogger, sneaker, jeans, chinos, cargo, parka, puffer, eşofman
- Required: a dress or suit saved under the "Dress / suit" category

---

## Data Storage

All data is stored in the browser's localStorage — nothing is sent to any external server except the weather API request. No account or login is required.

| Key | Contents |
|---|---|
| `styleai-photo` | Last uploaded or captured photo (base64) |
| `styleai-closet` | Array of closet items (max 60) |
| `styleai-saved` | Array of saved outfits (max 12) |

---

## Technical Notes

- The Python server serves all static files (HTML, CSS, JS) and handles `POST /api/recommend`.
- CORS headers are set on all responses so the app can also be tested from a different origin if needed.
- The JS fallback engine (`generateOutfit`) mirrors the Python logic exactly — same blocked keywords, same formality scoring, same missing category warnings — so the output is consistent whether or not the server is running.
- Weather data comes from the Open-Meteo free API. No API key is required.
- The app uses `DM Serif Display` and `DM Sans` from Google Fonts for typography.
