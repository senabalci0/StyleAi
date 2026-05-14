const state = {
  photo: localStorage.getItem("styleai-photo") || "",
  weather: null,
  recommendation: null,
  stream: null,
  saved: JSON.parse(localStorage.getItem("styleai-saved") || "[]"),
  closet: JSON.parse(localStorage.getItem("styleai-closet") || "[]"),
};

const daySelect = document.querySelector("#daySelect");
const photoInput = document.querySelector("#photoInput");
const previewImage = document.querySelector("#previewImage");
const emptyPhoto = document.querySelector("#emptyPhoto");
const cameraFeed = document.querySelector("#cameraFeed");
const cameraButton = document.querySelector("#cameraButton");
const captureButton = document.querySelector("#captureButton");
const clearPhotoButton = document.querySelector("#clearPhotoButton");
const snapshotCanvas = document.querySelector("#snapshotCanvas");
const styleForm = document.querySelector("#styleForm");
const weatherStatus = document.querySelector("#weatherStatus");
const weatherStrip = document.querySelector("#weatherStrip");
const weatherChip = document.querySelector("#weatherChip");
const chipTemp = document.querySelector("#chipTemp");
const chipSummary = document.querySelector("#chipSummary");
const outfitCard = document.querySelector("#outfitCard");
const saveOutfit = document.querySelector("#saveOutfit");
const rejectOutfit = document.querySelector("#rejectOutfit");
const savedList = document.querySelector("#savedList");
const refreshWeather = document.querySelector("#refreshWeather");
const clearSaved = document.querySelector("#clearSaved");
const closetName = document.querySelector("#closetName");
const closetCategory = document.querySelector("#closetCategory");
const addToCloset = document.querySelector("#addToCloset");
const closetGrid = document.querySelector("#closetGrid");
const clearCloset = document.querySelector("#clearCloset");

const categoryLabels = {
  top: "Top",
  bottom: "Bottom",
  outerwear: "Outerwear",
  shoes: "Shoes",
  accessory: "Accessory",
  dress: "Dress / suit",
};

const styleCopy = {
  daily: {
    label: "Casual",
    base: ["Plain T-shirt or light knit", "Relaxed jeans or chinos", "Clean sneakers", "Minimal watch or small accessory"],
    mood: "easy, polished, and comfortable all day",
  },
  sport: {
    label: "Sport",
    base: ["Breathable top", "Joggers or leggings", "Supportive sneakers", "Light zip layer"],
    mood: "active, light, and easy to move in",
  },
  smart: {
    label: "Smart",
    base: ["Shirt, blouse, or fine turtleneck", "Tailored trousers or midi skirt", "Loafers, boots, or refined sneakers", "Clean-lined jacket"],
    mood: "intentional, simple, and city-ready",
  },
  wedding: {
    label: "Wedding",
    base: ["Dress or suit", "Elegant shoes", "Subtle jewelry", "Photo-friendly finishing layer"],
    mood: "celebratory, elegant, and balanced",
  },
};

const weatherCodes = new Map([
  [0, "Clear"],
  [1, "Mostly clear"],
  [2, "Partly cloudy"],
  [3, "Cloudy"],
  [45, "Foggy"],
  [48, "Foggy"],
  [51, "Drizzle"],
  [53, "Drizzle"],
  [55, "Drizzle"],
  [61, "Rainy"],
  [63, "Rainy"],
  [65, "Heavy rain"],
  [71, "Snowy"],
  [73, "Snowy"],
  [75, "Heavy snow"],
  [80, "Showers"],
  [81, "Showers"],
  [82, "Heavy showers"],
  [95, "Stormy"],
]);

function localDateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function initDays() {
  const formatter = new Intl.DateTimeFormat("en-US", { weekday: "long", day: "numeric", month: "long" });
  const today = new Date();

  for (let index = 0; index < 7; index += 1) {
    const date = new Date(today);
    date.setDate(today.getDate() + index);
    const option = document.createElement("option");
    option.value = localDateKey(date);
    option.textContent = index === 0 ? `Today, ${formatter.format(date)}` : formatter.format(date);
    daySelect.append(option);
  }
}

function setPhoto(dataUrl) {
  state.photo = dataUrl;
  localStorage.setItem("styleai-photo", dataUrl);
  previewImage.src = dataUrl;
  previewImage.hidden = false;
  emptyPhoto.hidden = true;
  cameraFeed.hidden = true;
}

function clearPhoto() {
  state.photo = "";
  localStorage.removeItem("styleai-photo");
  previewImage.removeAttribute("src");
  previewImage.hidden = true;
  emptyPhoto.hidden = false;
  stopCamera();
}

function stopCamera() {
  if (state.stream) {
    state.stream.getTracks().forEach((track) => track.stop());
    state.stream = null;
  }
  cameraFeed.hidden = true;
  captureButton.hidden = true;
  cameraButton.hidden = false;
}

function renderWeather() {
  const weather = state.weather;
  if (!weather) {
    weatherStrip.innerHTML = "<span>--°C</span><span>Wind -- km/h</span><span>Rain --%</span>";
    chipTemp.textContent = "--°";
    chipSummary.textContent = "Waiting for location";
    return;
  }

  const summary = weatherCodes.get(weather.code) || "Variable";
  weatherStatus.textContent = `${weather.locationLabel} looks ${summary.toLowerCase()}. Last update: ${weather.updatedAt}.`;
  chipTemp.textContent = `${Math.round(weather.temp)}°`;
  chipSummary.textContent = summary;
  weatherChip.style.borderColor = weather.precip > 45 ? "var(--blue)" : "var(--line)";
  weatherStrip.innerHTML = `
    <span>${Math.round(weather.temp)}°C</span>
    <span>Wind ${Math.round(weather.wind)} km/h</span>
    <span>Rain ${Math.round(weather.precip)}%</span>
  `;
}

function nearestWeatherForSelection(hourly) {
  const selectedDate = daySelect.value;
  const startTime = document.querySelector("#startTime").value || "08:00";
  const target = `${selectedDate}T${startTime}`;
  const index = hourly.time.findIndex((time) => time >= target);
  const safeIndex = index >= 0 ? index : 0;

  return {
    temp: hourly.temperature_2m[safeIndex],
    wind: hourly.wind_speed_10m[safeIndex],
    precip: hourly.precipitation_probability[safeIndex] ?? 0,
    code: hourly.weather_code[safeIndex],
  };
}

async function loadWeatherForCoords(latitude, longitude, locationLabel) {
  const params = new URLSearchParams({
    latitude: latitude.toFixed(4),
    longitude: longitude.toFixed(4),
    hourly: "temperature_2m,precipitation_probability,weather_code,wind_speed_10m",
    timezone: "auto",
    forecast_days: "7",
    _: Date.now().toString(),
  });
  const response = await fetch(`https://api.open-meteo.com/v1/forecast?${params}`, { cache: "no-store" });
  if (!response.ok) throw new Error("weather request failed");
  const data = await response.json();
  state.weather = {
    ...nearestWeatherForSelection(data.hourly),
    locationLabel,
    updatedAt: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
  };
  renderWeather();
}

async function loadDefaultWeather() {
  weatherStatus.textContent = "Location unavailable; refreshing Istanbul weather...";
  try {
    await loadWeatherForCoords(41.0082, 28.9784, "Istanbul");
  } catch {
    weatherStatus.textContent = "Weather service is unavailable; using sample weather for now.";
    state.weather = fallbackWeather();
    renderWeather();
  }
}

function fetchWeather() {
  weatherStatus.textContent = "Loading weather...";
  refreshWeather.disabled = true;
  refreshWeather.textContent = "Refreshing";

  const finish = () => {
    refreshWeather.disabled = false;
    refreshWeather.textContent = "Refresh weather";
  };

  if (!navigator.geolocation) {
    loadDefaultWeather().finally(finish);
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async ({ coords }) => {
      try {
        await loadWeatherForCoords(coords.latitude, coords.longitude, "your current location");
      } catch {
        await loadDefaultWeather();
      } finally {
        finish();
      }
    },
    () => {
      loadDefaultWeather().finally(finish);
    },
    { enableHighAccuracy: false, timeout: 8000, maximumAge: 0 },
  );
}

function fallbackWeather() {
  return {
    temp: 18,
    wind: 12,
    precip: 20,
    code: 2,
    locationLabel: "sample location",
    updatedAt: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
  };
}

function buildWeatherAdvice(weather, prefs) {
  const pieces = [];
  if (weather.temp <= 7) pieces.push("heavy coat or wool overcoat", "scarf", "closed shoes");
  if (weather.temp > 7 && weather.temp <= 15) pieces.push("mid-weight jacket", "long-sleeve top");
  if (weather.temp > 15 && weather.temp <= 24) pieces.push("light jacket or shirt layer");
  if (weather.temp > 24) pieces.push("breathable lightweight fabric", "sunglasses");
  if (weather.precip >= 45 && prefs.rainReady) pieces.push("water-resistant outer layer", "umbrella");
  if (weather.wind >= 25) pieces.push("wind-stable layer");
  return pieces;
}

function piecesFromCloset(style, weather) {
  const byCategory = (category) => state.closet.filter((item) => item.category === category);
  const pick = (category) => {
    const list = byCategory(category);
    return list.length ? list[Math.floor(Math.random() * list.length)] : null;
  };
  const picks = [];

  if (style === "wedding") {
    picks.push(pick("dress") || pick("top"));
  } else {
    picks.push(pick("top"), pick("bottom"));
  }

  if (weather.temp <= 18 || weather.wind >= 20 || weather.precip >= 45) picks.push(pick("outerwear"));
  picks.push(pick("shoes"), pick("accessory"));
  return picks.filter(Boolean);
}

function generateOutfit(formData) {
  const style = formData.get("style");
  const startTime = document.querySelector("#startTime").value;
  const endTime = document.querySelector("#endTime").value;
  const dayText = daySelect.options[daySelect.selectedIndex].textContent;
  const prefs = {
    comfort: document.querySelector("#comfort").checked,
    rainReady: document.querySelector("#rainReady").checked,
    photoAware: document.querySelector("#photoAware").checked,
  };
  const weather = state.weather || fallbackWeather();
  const weatherPieces = buildWeatherAdvice(weather, prefs);
  const selectedStyle = styleCopy[style];
  const closetPieces = piecesFromCloset(style, weather);
  const closetNames = closetPieces.map((item) => `${categoryLabels[item.category]}: ${item.name}`);
  const photoNote = state.photo && prefs.photoAware
    ? "Use the uploaded photo as the anchor piece, then match the color and formality around it."
    : closetPieces.length
      ? "This recommendation uses pieces saved in your closet."
      : "Your closet has no matching pieces yet, so this uses general wardrobe suggestions.";

  return {
    id: crypto.randomUUID(),
    title: `${selectedStyle.label} outfit`,
    meta: `${dayText} ${startTime}-${endTime}`,
    summary: `${Math.round(weather.temp)}°C and ${weatherCodes.get(weather.code) || "variable"} weather: ${selectedStyle.mood}.`,
    items: [...closetNames, ...(closetNames.length ? [] : selectedStyle.base), ...weatherPieces],
    note: photoNote,
    image: closetPieces[0]?.image || state.photo,
    closetPieces,
    tags: [selectedStyle.label, `${Math.round(weather.temp)}°C`, closetPieces.length ? "From closet" : "General idea"],
    createdAt: new Date().toLocaleString("en-US"),
  };
}

async function generateOutfitWithPython(formData) {
  const style = formData.get("style");
  const startTime = document.querySelector("#startTime").value;
  const endTime = document.querySelector("#endTime").value;
  const dayText = daySelect.options[daySelect.selectedIndex].textContent;
  const prefs = {
    comfort: document.querySelector("#comfort").checked,
    rainReady: document.querySelector("#rainReady").checked,
    photoAware: document.querySelector("#photoAware").checked,
  };
  const response = await fetch("/api/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      style,
      startTime,
      endTime,
      dayText,
      prefs,
      weather: state.weather || fallbackWeather(),
      closet: state.closet,
      photo: state.photo,
      hasPhoto: Boolean(state.photo),
    }),
  });

  if (!response.ok) throw new Error("Python recommendation failed");
  return response.json();
}

function renderRecommendation(rec) {
  outfitCard.innerHTML = `
    <div>
      <div class="tag-row">${rec.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}</div>
      <h2>${rec.title}</h2>
      <p>${rec.summary}</p>
    </div>
    ${rec.closetPieces?.length ? `<div class="mini-closet">${rec.closetPieces.map((item) => `
      <figure>
        <img src="${item.image}" alt="${item.name}" />
        <figcaption>${item.name}</figcaption>
      </figure>
    `).join("")}</div>` : ""}
    <ul>${rec.items.map((item) => `<li>${item}</li>`).join("")}</ul>
    <p class="muted">${rec.note}</p>
  `;
  saveOutfit.disabled = false;
  rejectOutfit.disabled = false;
}

function renderSaved() {
  if (state.saved.length === 0) {
    savedList.innerHTML = '<p class="muted">No saved outfits yet.</p>';
    return;
  }

  savedList.innerHTML = state.saved.map((item) => `
    <article class="saved-item">
      ${item.image ? `<img src="${item.image}" alt="${item.title}" />` : "<div></div>"}
      <div>
        <strong>${item.title}</strong>
        <small>${item.meta} · ${item.createdAt}</small>
      </div>
    </article>
  `).join("");
}

function saveCloset() {
  localStorage.setItem("styleai-closet", JSON.stringify(state.closet));
}

function renderCloset() {
  if (state.closet.length === 0) {
    closetGrid.innerHTML = '<p class="muted">Your closet is empty. Upload or capture a photo, then add an item name and category.</p>';
    return;
  }

  closetGrid.innerHTML = state.closet.map((item) => `
    <article class="closet-item">
      <img src="${item.image}" alt="${item.name}" />
      <strong>${item.name}</strong>
      <small>${categoryLabels[item.category]}</small>
      <button type="button" data-remove-closet="${item.id}">Remove</button>
    </article>
  `).join("");
}

photoInput.addEventListener("change", (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.addEventListener("load", () => setPhoto(reader.result));
  reader.readAsDataURL(file);
});

cameraButton.addEventListener("click", async () => {
  try {
    state.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" }, audio: false });
    cameraFeed.srcObject = state.stream;
    cameraFeed.hidden = false;
    previewImage.hidden = true;
    emptyPhoto.hidden = true;
    captureButton.hidden = false;
    cameraButton.hidden = true;
  } catch {
    alert("Camera could not be opened. Check browser permission or use a localhost connection.");
  }
});

captureButton.addEventListener("click", () => {
  snapshotCanvas.width = cameraFeed.videoWidth || 900;
  snapshotCanvas.height = cameraFeed.videoHeight || 1200;
  const context = snapshotCanvas.getContext("2d");
  context.drawImage(cameraFeed, 0, 0, snapshotCanvas.width, snapshotCanvas.height);
  setPhoto(snapshotCanvas.toDataURL("image/jpeg", 0.88));
  stopCamera();
});

clearPhotoButton.addEventListener("click", clearPhoto);

addToCloset.addEventListener("click", () => {
  if (!state.photo) {
    alert("Upload or capture a clothing photo first.");
    return;
  }

  const category = closetCategory.value;
  const name = closetName.value.trim() || `${categoryLabels[category]} item`;
  state.closet = [
    {
      id: crypto.randomUUID(),
      name,
      category,
      image: state.photo,
      createdAt: new Date().toLocaleString("en-US"),
    },
    ...state.closet,
  ].slice(0, 60);

  saveCloset();
  renderCloset();
  closetName.value = "";
});

closetGrid.addEventListener("click", (event) => {
  const id = event.target.dataset.removeCloset;
  if (!id) return;
  state.closet = state.closet.filter((item) => item.id !== id);
  saveCloset();
  renderCloset();
});

styleForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.weather) state.weather = fallbackWeather();
  const submitButton = styleForm.querySelector(".generate-button");
  const originalText = submitButton.textContent;
  submitButton.disabled = true;
  submitButton.textContent = "Thinking...";

  try {
    state.recommendation = await generateOutfitWithPython(new FormData(styleForm));
  } catch {
    state.recommendation = generateOutfit(new FormData(styleForm));
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = originalText;
  }

  renderRecommendation(state.recommendation);
});

saveOutfit.addEventListener("click", () => {
  if (!state.recommendation) return;
  state.saved = [state.recommendation, ...state.saved].slice(0, 12);
  localStorage.setItem("styleai-saved", JSON.stringify(state.saved));
  renderSaved();
  saveOutfit.disabled = true;
});

rejectOutfit.addEventListener("click", () => {
  state.recommendation = null;
  outfitCard.innerHTML = '<p class="muted">Not saved. Generate a new outfit whenever you are ready.</p>';
  saveOutfit.disabled = true;
  rejectOutfit.disabled = true;
});

refreshWeather.addEventListener("click", fetchWeather);

clearSaved.addEventListener("click", () => {
  state.saved = [];
  localStorage.removeItem("styleai-saved");
  renderSaved();
});

clearCloset.addEventListener("click", () => {
  state.closet = [];
  localStorage.removeItem("styleai-closet");
  renderCloset();
});

daySelect.addEventListener("change", () => {
  if (state.weather) fetchWeather();
});

document.querySelector("#startTime").addEventListener("change", () => {
  if (state.weather) fetchWeather();
});

initDays();
if (state.photo) setPhoto(state.photo);
renderSaved();
renderCloset();
renderWeather();
fetchWeather();