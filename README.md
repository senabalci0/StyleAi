# StyleAI 👗

An AI-powered outfit planner that suggests clothing based on real-time weather, time of day, and your personal style preferences.

---

## Features

- 🌤️ Real-time weather integration (Open-Meteo API)
- 👔 Style modes: Casual, Sport, Smart, Wedding
- 📷 Photo upload & camera capture for wardrobe items
- 🗂️ Personal closet management (saved locally)
- 💾 Save or reject outfit recommendations
- 📱 Responsive design for mobile and desktop

---

## Project Structure

```
styleai/
├── index.html      # App layout and structure
├── style.css       # Styling and responsive design
├── app.js          # Frontend logic (weather, closet, UI)
└── app.py          # Flask backend (outfit generation)
```

---

## Setup & Installation

### 1. Install Python dependencies

```bash
pip install flask flask-cors
```

### 2. Start the Flask backend

```bash
python app.py
```

Flask will run on `http://127.0.0.1:5000`

### 3. Serve the frontend

Use VS Code Live Server or run:

```bash
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.


---

## How It Works

1. The app fetches weather data for your location using the Open-Meteo API
2. You select a day, time range, and style preference
3. The frontend sends your style and weather data to the Flask backend
4. Flask returns a curated outfit suggestion based on weather conditions
5. You can save outfits you like or dismiss ones you don't

---

## Requirements

- Python 3.8+
- Flask
- flask-cors
- A modern browser (Chrome, Firefox, Safari, Edge)

