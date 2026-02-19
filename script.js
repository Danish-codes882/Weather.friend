(function () {
  const form = document.getElementById("weather-form");
  const input = document.getElementById("city-input");
  const btn = document.getElementById("search-btn");
  const errorBanner = document.getElementById("error-banner");
  const results = document.getElementById("results");

  const el = (id) => document.getElementById(id);

  const UNSPLASH_SEEDS = [1, 47, 88];

  function setLoading(state) {
    btn.classList.toggle("loading", state);
    btn.disabled = state;
    input.disabled = state;
  }

  function showError(msg) {
    errorBanner.textContent = msg;
    errorBanner.classList.remove("hidden");
    results.classList.add("hidden");

    errorBanner.style.animation = "none";
    requestAnimationFrame(() => {
      errorBanner.style.animation = "";
    });
  }

  function hideError() {
    errorBanner.classList.add("hidden");
  }

  function renderList(ulId, items) {
    const ul = el(ulId);
    ul.innerHTML = "";
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item;
      ul.appendChild(li);
    });
  }

  function loadImage(imgEl, src, alt) {
    imgEl.classList.remove("loaded");
    imgEl.alt = alt;

    const tempImg = new Image();
    tempImg.onload = () => {
      imgEl.src = src;
      imgEl.classList.add("loaded");
    };
    tempImg.onerror = () => {
      imgEl.src = `https://source.unsplash.com/featured/800x600/?landscape,nature`;
      imgEl.classList.add("loaded");
    };
    tempImg.src = src;
  }

  function renderImages(city) {
    const encoded = encodeURIComponent(city);
    const queries = [`${encoded},city`, `${encoded},travel`, `${encoded},nature`];
    const ids = ["place-img-1", "place-img-2", "place-img-3"];
    const sizes = ["1200x900", "800x600", "800x600"];

    ids.forEach((id, i) => {
      const src = `https://source.unsplash.com/featured/${sizes[i]}/?${queries[i]}&sig=${UNSPLASH_SEEDS[i]}${Date.now()}`;
      loadImage(el(id), src, `${city} — photo ${i + 1}`);
    });
  }

  function renderWeather(data) {
    el("city-name").textContent = data.city;
    el("country-name").textContent = data.country;
    el("temperature").textContent = data.temperature;
    el("description").textContent = data.description;
    el("feels-like").textContent = `${data.feels_like}°C`;
    el("humidity").textContent = `${data.humidity}%`;
    el("wind").textContent = `${data.wind_kmph} km/h`;

    const s = data.suggestions;
    renderList("clothing-list", s.clothing);
    renderList("accessories-list", s.accessories);
    renderList("travel-list", s.travel);
    renderList("health-list", s.health);

    renderImages(data.city);

    results.classList.remove("hidden");
    results.style.animation = "none";
    requestAnimationFrame(() => {
      results.style.animation = "fadeUp 0.6s ease both";
    });

    results.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const city = input.value.trim();
    if (!city) return;

    hideError();
    setLoading(true);

    try {
      const response = await fetch("/get-weather", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ city }),
      });

      const data = await response.json();

      if (!response.ok) {
        showError(data.error || "City not found or weather service unavailable.");
        return;
      }

      renderWeather(data);
    } catch {
      showError("Network error. Please check your connection and try again.");
    } finally {
      setLoading(false);
    }
  });
})();
