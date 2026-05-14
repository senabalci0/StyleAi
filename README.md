# StyleAI

A browser prototype for uploading or capturing clothing photos, saving wardrobe items, checking weather for a selected day and time range, and generating outfit recommendations.

## Run with Python

Camera and location permissions work best through `localhost`:

```powershell
python server.py
```

Then open:

```text
http://127.0.0.1:5173
```

No external Python package is required. The Python server serves the HTML, CSS,
and JavaScript files, and also provides `/api/recommend` for outfit suggestions.
If you open the project as plain static files, the browser will still use the
JavaScript fallback recommendation engine.

## PyCharm

1. Open this folder in PyCharm.
2. Open `server.py`.
3. Press Run.
4. Visit `http://127.0.0.1:5173`.

## Features

- Upload photos
- Take photos with the camera
- Save clothing items into My Closet with categories
- Use closet items when generating outfit recommendations
- Store photos, closet items, and saved outfits locally in the browser
- Select day and time range
- Choose Casual, Sport, Smart, or Wedding styles
- Fetch weather from Open-Meteo with location permission
- Fall back to Istanbul weather if location is unavailable
- Suggest layers, rain items, wind-friendly pieces, and temperature-aware outfits

## Closet Flow

1. Upload a clothing photo or take one with the camera.
2. Enter an item name.
3. Choose Top, Bottom, Outerwear, Shoes, Accessory, or Dress / suit.
4. Press `Add to closet`.
5. The app will try to build outfits using saved closet items.

   test123