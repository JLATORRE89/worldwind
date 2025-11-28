(function () {
  const canvas = document.getElementById("canvasOne");
  const apiInput = document.getElementById("apiInput");
  const connectBtn = document.getElementById("connectBtn");
  const statusText = document.getElementById("statusText");
  const baseInfo = document.getElementById("baseInfo");
  const unitList = document.getElementById("unitList");

  function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    if (window.wwd) {
      window.wwd.redraw();
    }
  }
  window.addEventListener("resize", resizeCanvas);
  resizeCanvas();

  const wwd = new WorldWind.WorldWindow("canvasOne");
  window.wwd = wwd;

  [
    new WorldWind.BMNGOneImageLayer(),
    new WorldWind.BMNGLandsatLayer(),
    new WorldWind.CompassLayer(),
    new WorldWind.CoordinatesDisplayLayer(wwd),
    new WorldWind.ViewControlsLayer(wwd),
  ].forEach((layer) => wwd.addLayer(layer));

  const baseLayer = new WorldWind.RenderableLayer("Base Station");
  const unitLayer = new WorldWind.RenderableLayer("Units");
  wwd.addLayer(baseLayer);
  wwd.addLayer(unitLayer);

  const state = {
    apiUrl: apiInput.value.trim(),
    timer: null,
  };

  connectBtn.addEventListener("click", () => {
    state.apiUrl = apiInput.value.trim();
    if (!state.apiUrl) {
      statusText.textContent = "Please enter an API URL.";
      return;
    }
    statusText.textContent = "Connecting…";
    fetchUnits(true);
  });

  function colorForDistance(distance) {
    const normalized = Math.min(distance / 150.0, 1.0);
    const r = normalized;
    const g = 1.0 - normalized;
    return new WorldWind.Color(r, g, 0.1, 0.9);
  }

  function updateBaseMarker(base) {
    baseLayer.removeAllRenderables();
    if (!base || base.lat === undefined || base.lon === undefined) {
      return;
    }
    const attrs = new WorldWind.PlacemarkAttributes(null);
    attrs.imageColor = WorldWind.Color.CYAN;
    attrs.labelAttributes.color = WorldWind.Color.CYAN;
    attrs.imageScale = 1.0;
    attrs.imageSource =
      WorldWind.configuration.baseUrl + "images/pushpins/plain-yellow.png";
    const placemark = new WorldWind.Placemark(
      new WorldWind.Position(base.lat, base.lon, 10),
      false,
      attrs
    );
    placemark.label = `Base Station\nLat ${base.lat.toFixed(
      5
    )} Lon ${base.lon.toFixed(5)}`;
    placemark.alwaysOnTop = true;
    baseLayer.addRenderable(placemark);
    baseInfo.textContent = `Base @ ${base.lat.toFixed(4)}, ${base.lon.toFixed(
      4
    )}`;
  }

  function updateUnits(units) {
    unitLayer.removeAllRenderables();
    unitList.innerHTML = "";
    units.forEach((unit) => {
      const attrs = new WorldWind.PlacemarkAttributes(null);
      attrs.imageSource =
        WorldWind.configuration.baseUrl + "images/pushpins/plain-red.png";
      attrs.imageScale = 0.8;
      attrs.imageColor = colorForDistance(unit.distance_m || 0.0);
      const pos = new WorldWind.Position(unit.lat, unit.lon, 50);
      const placemark = new WorldWind.Placemark(pos, false, attrs);
      const distance = (unit.distance_m || 0).toFixed(1);
      placemark.label = `${unit.id}\n${distance} m\nRSSI ${Math.round(
        unit.rssi || 0
      )} dBm`;
      placemark.alwaysOnTop = true;
      unitLayer.addRenderable(placemark);

      const li = document.createElement("li");
      li.textContent = `${unit.id}: ${distance} m @ ${Math.round(
        unit.bearing_deg || 0
      )}° (RSSI ${Math.round(unit.rssi || 0)} dBm)`;
      unitList.appendChild(li);
    });
  }

  async function fetchUnits(force) {
    if (!state.apiUrl) {
      return;
    }
    try {
      const response = await fetch(state.apiUrl, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      updateBaseMarker(data.base || {});
      updateUnits(data.units || []);
      statusText.textContent = `Updated ${new Date().toLocaleTimeString()}`;
      wwd.redraw();
    } catch (err) {
      console.error(err);
      statusText.textContent = `Error fetching data: ${err}`;
    } finally {
      if (force && state.timer) {
        clearInterval(state.timer);
        state.timer = null;
      }
      if (!state.timer) {
        state.timer = setInterval(fetchUnits, 5000);
      }
    }
  }

  // Auto-connect on load with default value.
  fetchUnits(true);
})();
