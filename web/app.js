const state = {
  manifest: null,
  run: null,
  summary: null,
  rows: [],
  events: [],
  years: [],
  countries: [],
  selectedYear: null,
  selectedMetric: "flourishing",
};

const metricMeta = {
  flourishing: { label: "Flourishing", color: "#72e6b3" },
  conflict_risk: { label: "Conflict Risk", color: "#ff8b5d" },
  legitimacy: { label: "Legitimacy", color: "#56c6ff" },
  trust: { label: "Trust", color: "#a5c7ff" },
  treasury: { label: "Treasury", color: "#ffcc67" },
  economic_output: { label: "Output", color: "#ff9a52" },
};

const countryPalette = ["#56c6ff", "#ff8b5d", "#72e6b3", "#ffcc67", "#b58cff", "#ff5f8a"];

const elements = {
  scenarioTitle: document.getElementById("scenarioTitle"),
  scenarioSubtitle: document.getElementById("scenarioSubtitle"),
  runSelect: document.getElementById("runSelect"),
  yearsRange: document.getElementById("yearsRange"),
  eventCount: document.getElementById("eventCount"),
  countryCount: document.getElementById("countryCount"),
  yearLabel: document.getElementById("yearLabel"),
  yearSlider: document.getElementById("yearSlider"),
  metricSwitcher: document.getElementById("metricSwitcher"),
  constellationSvg: document.getElementById("constellationSvg"),
  trendSvg: document.getElementById("trendSvg"),
  chartTitle: document.getElementById("chartTitle"),
  chartLegend: document.getElementById("chartLegend"),
  countryCards: document.getElementById("countryCards"),
  eventFeed: document.getElementById("eventFeed"),
  cardTemplate: document.getElementById("countryCardTemplate"),
};

async function init() {
  try {
    const manifestResponse = await fetch("./runs/index.json", { cache: "no-store" });
    if (!manifestResponse.ok) {
      throw new Error("Run manifest not found. Generate it with `python -m civlab.cli refresh-dashboard` or rerun a scenario.");
    }
    state.manifest = await manifestResponse.json();
    if (!state.manifest.runs.length) {
      throw new Error("No runs available yet. Run a scenario first.");
    }
    buildRunSelector();
    const requestedRun = new URLSearchParams(window.location.search).get("run");
    const run = state.manifest.runs.find((item) => item.slug === requestedRun) || state.manifest.runs[0];
    elements.runSelect.value = run.slug;
    await loadRun(run.slug);
    wireEvents();
  } catch (error) {
    renderEmpty(error.message);
  }
}

function buildRunSelector() {
  elements.runSelect.innerHTML = "";
  for (const run of state.manifest.runs) {
    const option = document.createElement("option");
    option.value = run.slug;
    option.textContent = `${run.scenario_name} [${run.slug}]`;
    elements.runSelect.appendChild(option);
  }
}

function wireEvents() {
  elements.runSelect.addEventListener("change", async (event) => {
    await loadRun(event.target.value);
  });

  elements.yearSlider.addEventListener("input", (event) => {
    state.selectedYear = Number(event.target.value);
    render();
  });
}

async function loadRun(slug) {
  const run = state.manifest.runs.find((item) => item.slug === slug);
  if (!run) {
    return;
  }

  const [summaryResponse, rowsResponse, eventsResponse] = await Promise.all([
    fetch(run.summary_path, { cache: "no-store" }),
    fetch(run.country_year_path, { cache: "no-store" }),
    fetch(run.events_path, { cache: "no-store" }),
  ]);
  if (!summaryResponse.ok || !rowsResponse.ok || !eventsResponse.ok) {
    throw new Error(`Run assets for ${slug} are incomplete or unavailable.`);
  }

  state.run = run;
  state.summary = await summaryResponse.json();
  state.rows = parseCSV(await rowsResponse.text()).map((row) => ({
    ...row,
    year: Number(row.year),
    economic_output: Number(row.economic_output),
    flourishing: Number(row.flourishing),
    legitimacy: Number(row.legitimacy),
    trust: Number(row.trust),
    inequality: Number(row.inequality),
    polarization: Number(row.polarization),
    conflict_risk: Number(row.conflict_risk),
    external_threat: Number(row.external_threat),
    treasury: Number(row.treasury),
    population: Number(row.population),
  }));
  state.events = parseJSONL(await eventsResponse.text()).map((event) => ({
    ...event,
    year: Number(event.year),
    severity: Number(event.severity),
  }));
  state.years = [...new Set(state.rows.map((row) => row.year))].sort((left, right) => left - right);
  state.countries = [...new Set(state.rows.map((row) => row.iso3))].sort();
  state.selectedYear = state.years[state.years.length - 1];
  const url = new URL(window.location.href);
  url.searchParams.set("run", slug);
  window.history.replaceState({}, "", url);
  syncYearSlider();
  renderMetricButtons();
  render();
}

function syncYearSlider() {
  elements.yearSlider.min = String(state.years[0]);
  elements.yearSlider.max = String(state.years[state.years.length - 1]);
  elements.yearSlider.step = "1";
  elements.yearSlider.value = String(state.selectedYear);
}

function renderMetricButtons() {
  elements.metricSwitcher.innerHTML = "";
  for (const [metric, meta] of Object.entries(metricMeta)) {
    const button = document.createElement("button");
    button.className = `metric-button${metric === state.selectedMetric ? " active" : ""}`;
    button.textContent = meta.label;
    button.addEventListener("click", () => {
      state.selectedMetric = metric;
      renderMetricButtons();
      renderTrendChart();
      renderCountryCards();
    });
    elements.metricSwitcher.appendChild(button);
  }
}

function render() {
  if (!state.rows.length) {
    return;
  }

  const selectedRows = rowsForYear(state.selectedYear);
  elements.scenarioTitle.textContent = state.summary.scenario_name;
  elements.scenarioSubtitle.textContent = `${state.run.slug} - ${state.summary.steps} years - browser dashboard`;
  elements.yearsRange.textContent = `${state.summary.start_year}-${state.summary.final_year}`;
  elements.eventCount.textContent = String(state.summary.event_count);
  elements.countryCount.textContent = String(state.countries.length);
  elements.yearLabel.textContent = String(state.selectedYear);

  renderConstellation(selectedRows);
  renderTrendChart();
  renderCountryCards();
  renderEvents();
}

function renderConstellation(selectedRows) {
  const svg = elements.constellationSvg;
  svg.innerHTML = "";
  if (!selectedRows.length) {
    return;
  }

  const width = 800;
  const height = 520;
  const centerX = width / 2;
  const centerY = height / 2;
  const orbit = Math.min(width, height) * 0.33;
  const yearEvents = state.events.filter((event) => event.year === state.selectedYear);

  appendSvg(svg, "circle", { cx: centerX, cy: centerY, r: orbit + 78, fill: "rgba(86,198,255,0.06)" });
  appendSvg(svg, "circle", { cx: centerX, cy: centerY, r: orbit + 18, fill: "none", stroke: "rgba(255,255,255,0.08)", "stroke-dasharray": "5 9" });

  const positioned = selectedRows.map((row, index) => {
    const angle = (Math.PI * 2 * index) / selectedRows.length - Math.PI / 2;
    const x = centerX + Math.cos(angle) * orbit;
    const y = centerY + Math.sin(angle) * (orbit * 0.82);
    return { ...row, x, y, color: countryColor(row.iso3) };
  });

  for (let i = 0; i < positioned.length; i += 1) {
    for (let j = i + 1; j < positioned.length; j += 1) {
      const left = positioned[i];
      const right = positioned[j];
      const conflict = (left.conflict_risk + right.conflict_risk) / 2;
      const thisYearEvents = yearEvents.filter((event) => event.actors.includes(left.iso3) && event.actors.includes(right.iso3));
      const stroke = thisYearEvents.some((event) => event.event_type.includes("war"))
        ? "rgba(255,95,95,0.88)"
        : `rgba(255, 139, 93, ${0.14 + conflict * 0.72})`;
      appendSvg(svg, "line", {
        x1: left.x,
        y1: left.y,
        x2: right.x,
        y2: right.y,
        stroke,
        "stroke-width": String(1 + conflict * 8),
      });
    }
  }

  for (const row of positioned) {
    const radius = 22 + normalize(row.population, 0, maxValue(selectedRows, "population")) * 26;
    appendSvg(svg, "circle", {
      cx: row.x,
      cy: row.y,
      r: radius + 10,
      fill: "none",
      stroke: withAlpha(row.color, 0.34 + clamp01(row.flourishing) * 0.5),
      "stroke-width": String(6 + clamp01(row.flourishing) * 8),
    });
    appendSvg(svg, "circle", {
      cx: row.x,
      cy: row.y,
      r: radius,
      fill: withAlpha("#08111f", 0.9),
      stroke: withAlpha(row.color, 0.9),
      "stroke-width": "2.5",
    });
    appendSvg(svg, "circle", {
      cx: row.x,
      cy: row.y,
      r: Math.max(8, radius * clamp01(row.legitimacy)),
      fill: withAlpha("#ffcc67", 0.5 + clamp01(row.legitimacy) * 0.4),
    });
    appendSvg(svg, "text", {
      x: row.x,
      y: row.y - radius - 16,
      fill: row.color,
      "font-size": "12",
      "text-anchor": "middle",
      "letter-spacing": "1.6",
    }, row.iso3);
    appendSvg(svg, "text", {
      x: row.x,
      y: row.y + 5,
      fill: "#edf4fb",
      "font-size": "14",
      "font-weight": "700",
      "text-anchor": "middle",
    }, row.country);
    appendSvg(svg, "text", {
      x: row.x,
      y: row.y + 24,
      fill: "#95a8ba",
      "font-size": "11",
      "text-anchor": "middle",
    }, `F ${formatScore(row.flourishing)} | C ${formatScore(row.conflict_risk)}`);
  }
}

function renderTrendChart() {
  const svg = elements.trendSvg;
  svg.innerHTML = "";
  const metric = state.selectedMetric;
  const rowsByCountry = groupBy(state.rows, (row) => row.iso3);
  const width = 760;
  const height = 320;
  const margin = { top: 22, right: 18, bottom: 34, left: 48 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;
  const values = state.rows.map((row) => row[metric]);
  const minValue = metric === "treasury" || metric === "economic_output" ? 0 : Math.min(0, ...values);
  const maxMetric = Math.max(...values, 0.01);
  const yearMin = state.years[0];
  const yearMax = state.years[state.years.length - 1];

  elements.chartTitle.textContent = `${metricMeta[metric].label} across time`;

  appendSvg(svg, "rect", {
    x: 0,
    y: 0,
    width,
    height,
    fill: "rgba(255,255,255,0.02)",
    rx: 18,
  });

  for (let tick = 0; tick <= 4; tick += 1) {
    const y = margin.top + (innerHeight / 4) * tick;
    appendSvg(svg, "line", {
      x1: margin.left,
      y1: y,
      x2: width - margin.right,
      y2: y,
      stroke: "rgba(255,255,255,0.07)",
    });
    const value = maxMetric - ((maxMetric - minValue) / 4) * tick;
    appendSvg(svg, "text", {
      x: 10,
      y: y + 4,
      fill: "#95a8ba",
      "font-size": "11",
    }, formatAxisValue(metric, value));
  }

  for (const year of state.years) {
    const x = scale(year, yearMin, yearMax, margin.left, width - margin.right);
    appendSvg(svg, "line", {
      x1: x,
      y1: margin.top,
      x2: x,
      y2: height - margin.bottom,
      stroke: "rgba(255,255,255,0.04)",
    });
    appendSvg(svg, "text", {
      x,
      y: height - 8,
      fill: "#95a8ba",
      "font-size": "11",
      "text-anchor": "middle",
    }, String(year));
  }

  const focusX = scale(state.selectedYear, yearMin, yearMax, margin.left, width - margin.right);
  appendSvg(svg, "line", {
    x1: focusX,
    y1: margin.top,
    x2: focusX,
    y2: height - margin.bottom,
    stroke: "rgba(255,204,103,0.65)",
    "stroke-width": "2",
  });

  elements.chartLegend.innerHTML = "";
  Object.values(rowsByCountry).forEach((rows, index) => {
    const color = countryColor(rows[0].iso3);
    const points = rows
      .sort((left, right) => left.year - right.year)
      .map((row) => {
        const x = scale(row.year, yearMin, yearMax, margin.left, width - margin.right);
        const y = scale(row[metric], minValue, maxMetric, height - margin.bottom, margin.top);
        return `${x},${y}`;
      })
      .join(" ");
    appendSvg(svg, "polyline", {
      points,
      fill: "none",
      stroke: color,
      "stroke-width": "3.5",
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
    });

    const selected = rows.find((row) => row.year === state.selectedYear);
    if (selected) {
      appendSvg(svg, "circle", {
        cx: scale(selected.year, yearMin, yearMax, margin.left, width - margin.right),
        cy: scale(selected[metric], minValue, maxMetric, height - margin.bottom, margin.top),
        r: 6,
        fill: color,
        stroke: "#08111f",
        "stroke-width": "2",
      });
    }

    const chip = document.createElement("div");
    chip.className = "legend-chip";
    chip.innerHTML = `<span class="legend-swatch" style="background:${color}"></span><span>${rows[0].country}</span>`;
    elements.chartLegend.appendChild(chip);
  });
}

function renderCountryCards() {
  elements.countryCards.innerHTML = "";
  const selectedRows = rowsForYear(state.selectedYear);
  const previousRows = rowsForYear(state.selectedYear - 1);
  const previousByIso = Object.fromEntries(previousRows.map((row) => [row.iso3, row]));
  const treasuryMax = maxValue(selectedRows, "treasury");

  for (const row of selectedRows) {
    const card = elements.cardTemplate.content.firstElementChild.cloneNode(true);
    card.querySelector(".country-name").textContent = row.country;
    card.querySelector(".country-iso").textContent = row.iso3;

    const previous = previousByIso[row.iso3];
    const delta = previous ? row.flourishing - previous.flourishing : 0;
    const chip = card.querySelector(".delta-chip");
    chip.textContent = `${delta >= 0 ? "+" : ""}${delta.toFixed(2)} F`;
    chip.classList.toggle("negative", delta < 0);

    const metrics = [
      { label: "Flourishing", value: row.flourishing, normalized: clamp01(row.flourishing) },
      { label: "Conflict", value: row.conflict_risk, normalized: clamp01(row.conflict_risk) },
      { label: "Legitimacy", value: row.legitimacy, normalized: clamp01(row.legitimacy) },
      { label: "Trust", value: row.trust, normalized: clamp01(row.trust) },
      { label: "Treasury", value: row.treasury, normalized: normalize(row.treasury, 0, treasuryMax), format: formatCompactNumber },
      { label: "Population", value: row.population, normalized: normalize(row.population, 0, maxValue(selectedRows, "population")), format: formatCompactNumber },
    ];

    const metricStack = card.querySelector(".metric-stack");
    for (const metric of metrics) {
      const rowEl = document.createElement("div");
      rowEl.className = "metric-row";
      const formatted = metric.format ? metric.format(metric.value) : formatScore(metric.value);
      rowEl.innerHTML = `
        <span class="metric-label">${metric.label}</span>
        <div class="metric-bar"><div class="metric-fill" style="width:${metric.normalized * 100}%"></div></div>
        <span class="metric-value">${formatted}</span>
      `;
      metricStack.appendChild(rowEl);
    }

    elements.countryCards.appendChild(card);
  }
}

function renderEvents() {
  elements.eventFeed.innerHTML = "";
  const yearEvents = state.events.filter((event) => event.year === state.selectedYear);
  if (!yearEvents.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No discrete events recorded for this year. Move the timeline or inspect trend trajectories.";
    elements.eventFeed.appendChild(empty);
    return;
  }

  for (const event of yearEvents) {
    const card = document.createElement("article");
    card.className = "event-card";
    card.innerHTML = `
      <div class="event-topline">
        <span class="event-type">${event.event_type.replaceAll("_", " ")}</span>
        <span class="event-severity">severity ${event.severity.toFixed(2)}</span>
      </div>
      <p>${formatActors(event.actors)} - ${event.detail}</p>
    `;
    elements.eventFeed.appendChild(card);
  }
}

function rowsForYear(year) {
  return state.rows.filter((row) => row.year === year).sort((left, right) => left.country.localeCompare(right.country));
}

function parseJSONL(text) {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => JSON.parse(line));
}

function parseCSV(text) {
  const rows = [];
  let current = "";
  let row = [];
  let insideQuotes = false;
  const normalized = text.replace(/\r\n/g, "\n");

  for (let index = 0; index < normalized.length; index += 1) {
    const char = normalized[index];
    const next = normalized[index + 1];

    if (char === "\"") {
      if (insideQuotes && next === "\"") {
        current += "\"";
        index += 1;
      } else {
        insideQuotes = !insideQuotes;
      }
      continue;
    }

    if (char === "," && !insideQuotes) {
      row.push(current);
      current = "";
      continue;
    }

    if (char === "\n" && !insideQuotes) {
      row.push(current);
      rows.push(row);
      row = [];
      current = "";
      continue;
    }

    current += char;
  }

  if (current.length || row.length) {
    row.push(current);
    rows.push(row);
  }

  const [header, ...body] = rows;
  return body.map((values) =>
    Object.fromEntries(header.map((column, index) => [column, values[index] ?? ""]))
  );
}

function groupBy(items, keyFn) {
  const grouped = {};
  for (const item of items) {
    const key = keyFn(item);
    grouped[key] = grouped[key] || [];
    grouped[key].push(item);
  }
  return grouped;
}

function normalize(value, minValue, maxValue) {
  if (!Number.isFinite(value)) {
    return 0;
  }
  if (maxValue <= minValue) {
    return 0;
  }
  return clamp01((value - minValue) / (maxValue - minValue));
}

function scale(value, minValue, maxValue, minOut, maxOut) {
  if (maxValue <= minValue) {
    return minOut;
  }
  return minOut + ((value - minValue) / (maxValue - minValue)) * (maxOut - minOut);
}

function maxValue(rows, key) {
  return Math.max(...rows.map((row) => row[key]), 0.0001);
}

function appendSvg(svg, tag, attrs, textContent) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", tag);
  Object.entries(attrs).forEach(([key, value]) => element.setAttribute(key, value));
  if (textContent) {
    element.textContent = textContent;
  }
  svg.appendChild(element);
  return element;
}

function countryColor(iso3) {
  const index = state.countries.indexOf(iso3);
  return countryPalette[index % countryPalette.length];
}

function clamp01(value) {
  return Math.max(0, Math.min(1, value));
}

function withAlpha(hex, alpha) {
  const normalized = hex.replace("#", "");
  const chunk = normalized.length === 3
    ? normalized.split("").map((char) => char + char)
    : normalized.match(/.{1,2}/g);
  const [red, green, blue] = chunk.map((value) => parseInt(value, 16));
  return `rgba(${red}, ${green}, ${blue}, ${alpha})`;
}

function formatScore(value) {
  return value.toFixed(2);
}

function formatCompactNumber(value) {
  return new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

function formatAxisValue(metric, value) {
  if (metric === "treasury" || metric === "population") {
    return formatCompactNumber(value);
  }
  return value.toFixed(2);
}

function formatActors(actors) {
  if (!actors || !actors.length) {
    return "Unknown actors";
  }
  if (actors.length === 1) {
    return actors[0];
  }
  if (actors.length === 2) {
    return `${actors[0]} vs ${actors[1]}`;
  }
  return actors.join(", ");
}

function renderEmpty(message) {
  elements.scenarioTitle.textContent = "Dashboard unavailable";
  elements.scenarioSubtitle.textContent = message;
  elements.countryCards.innerHTML = `<div class="empty-state">${message}</div>`;
  elements.eventFeed.innerHTML = `<div class="empty-state">Generate a run manifest and refresh the page.</div>`;
}

init();
