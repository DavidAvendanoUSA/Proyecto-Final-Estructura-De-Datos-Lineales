// main.js - visualización mejorada sin dependencias
// Cambios: ya no se muestra JSON crudo al recibir /simulacion/result y se removió el botón
// "Ver resultado". La visualización genera una nota que indica que los números en el eje X son ticks (unidad de tiempo).

const el = (id) => document.getElementById(id);
const result = el("result");
const preparingSection = el("preparingSection");
const preparingText = el("preparingText");
const vizContainer = el("vizContainer");

function show(text) {
  if (result) result.textContent = text;
  console.log("[UI]", text);
}

function showPreparing(text) {
  if (preparingSection) preparingSection.style.display = "block";
  if (preparingText) preparingText.textContent = text;
}

function hidePreparing() {
  if (preparingSection) preparingSection.style.display = "none";
}

function isNumberString(s) {
  return s !== "" && !Number.isNaN(Number(s));
}

function buildProbObject(prefix) {
  const aEl = el(`${prefix}_A`);
  const mEl = el(`${prefix}_M`);
  const bEl = el(`${prefix}_B`);
  const aVal = aEl ? aEl.value.trim() : "";
  const mVal = mEl ? mEl.value.trim() : "";
  const bVal = bEl ? bEl.value.trim() : "";
  if (aVal === "" && mVal === "" && bVal === "") return null;
  if (!isNumberString(aVal) || !isNumberString(mVal) || !isNumberString(bVal)) {
    return {
      error: `Todos los valores ${prefix}_A/M/B deben ser números entre 0 y 1.`,
    };
  }
  return { A: Number(aVal), M: Number(mVal), B: Number(bVal) };
}

function validateInputs(tiempo, probLlegadaObj, probServicioObj) {
  if (tiempo !== null) {
    if (typeof tiempo !== "number" || !Number.isFinite(tiempo) || tiempo < 0) {
      return { ok: false, message: "Tiempo debe ser un número >= 0." };
    }
  }
  function checkProb(obj, name) {
    if (obj === null) return { ok: true };
    if (obj.error) return { ok: false, message: obj.error };
    for (const k of ["A", "M", "B"]) {
      if (!(k in obj))
        return { ok: false, message: `${name} debe tener la clave ${k}.` };
      const v = Number(obj[k]);
      if (Number.isNaN(v) || v < 0 || v > 1)
        return { ok: false, message: `${name}.${k} debe estar en 0..1.` };
    }
    return { ok: true };
  }
  const a = checkProb(probLlegadaObj, "prob_llegada");
  if (!a.ok) return a;
  const b = checkProb(probServicioObj, "prob_servicio");
  if (!b.ok) return b;
  return { ok: true };
}

async function fetchJson(method, path, body = null) {
  try {
    const options = {
      method,
      headers: { "Content-Type": "application/json" },
      cache: "no-store",
    };
    if (method !== "GET" && method !== "HEAD")
      options.body = body !== null ? JSON.stringify(body) : JSON.stringify({});
    const resp = await fetch(path, options);
    const contentType = resp.headers.get("content-type") || "";
    const text = await resp.text();
    const parsed =
      contentType.includes("application/json") && text
        ? JSON.parse(text)
        : text;
    return { ok: resp.ok, status: resp.status, body: parsed };
  } catch (err) {
    console.error("[fetchJson] error", err);
    return { error: true, message: err.message || String(err) };
  }
}

// humanize: legible para respuestas excepto result (result se visualiza)
function humanize(path, res) {
  if (!res || res.error)
    return `Error: ${res ? res.message : "respuesta inválida"}`;
  if (path === "/simulacion/status") {
    const s = res.body;
    return `Estado: ${s.running ? "Ejecutando" : "Detenida"}${
      s.pausado ? " (Pausada)" : ""
    }\nTiempo total: ${s.tiempo_total}\nClientes en cola: ${
      s.cola_tamaño
    }\nEventos registrados: ${s.logs_count}`;
  }
  if (path === "/simulacion/start") {
    if (res.status === 201 || (res.body && res.body.started)) {
      const id =
        res.body && res.body.corrida_id
          ? ` (corrida_id: ${res.body.corrida_id})`
          : "";
      return `Simulación iniciada correctamente${id}.`;
    }
    if (
      res.status === 409 &&
      res.body &&
      res.body.reason === "already_running"
    ) {
      return "No se pudo iniciar: ya hay una simulación en ejecución.";
    }
    return `Inicio no completado: HTTP ${res.status} - ${JSON.stringify(
      res.body
    )}`;
  }
  if (path === "/simulacion/pause")
    return res.ok
      ? "Simulación pausada."
      : `Error al pausar: HTTP ${res.status}`;
  if (path === "/simulacion/resume")
    return res.ok
      ? "Simulación reanudada."
      : `Error al reanudar: HTTP ${res.status}`;
  if (path === "/simulacion/stop")
    return res.ok
      ? "Simulación detenida."
      : `Error al detener: HTTP ${res.status}`;
  if (path === "/simulacion/restore")
    return res.ok
      ? "Parámetros restaurados."
      : `Error al restaurar: HTTP ${res.status}`;
  try {
    return `Respuesta (${path})\n${JSON.stringify(res.body, null, 2)}`;
  } catch (e) {
    return `Respuesta (${path}) - no printable`;
  }
}

// Mostrar resultados: no mostramos JSON crudo; creamos visual y resumen
function displayResponseFor(path, res) {
  if (res.error) {
    show(`Error de red: ${res.message}`);
    return;
  }
  if (path === "/simulacion/result") {
    const stats =
      res.body && res.body.estadisticas ? res.body.estadisticas : null;
    if (stats) {
      show(
        `Simulación terminada — llegados/atendidos por tipo: A:${stats.A.llegaron}/${stats.A.atendidos}  M:${stats.M.llegaron}/${stats.M.atendidos}  B:${stats.B.llegaron}/${stats.B.atendidos}`
      );
    } else {
      show(
        'Simulación terminada. Nota: los números en el eje X son "ticks" (unidad de tiempo).'
      );
    }
    try {
      renderResultVisualization(res.body);
    } catch (err) {
      console.error("renderResultVisualization error:", err);
    }
  } else {
    show(humanize(path, res));
  }
}

// ---------------- Visualization helpers ----------------

function clearViz() {
  if (!vizContainer) return;
  vizContainer.innerHTML = "";
  vizContainer.style.position = "relative";
}

function getTooltip() {
  let tip = vizContainer.querySelector(".viz-tooltip");
  if (!tip) {
    tip = document.createElement("div");
    tip.className = "viz-tooltip";
    tip.setAttribute(
      "style",
      "position:absolute; display:none; pointer-events:none; padding:6px; background:#fff; border:1px solid #888; font-size:12px; color:#000; border-radius:4px; box-shadow:2px 2px 6px rgba(0,0,0,0.12); z-index:999;"
    );
    vizContainer.appendChild(tip);
  }
  return tip;
}

function intervalsOverlap(a1, a2, b1, b2) {
  return !(a2 <= b1 || b2 <= a1);
}

function renderResultVisualization(result) {
  clearViz();
  if (!vizContainer) return;
  const historial = result && result.historial ? result.historial : [];
  if (!Array.isArray(historial) || historial.length === 0) {
    const p = document.createElement("pre");
    p.textContent = "No hay historial para visualizar. (Simulación terminada.)";
    vizContainer.appendChild(p);
    return;
  }

  let minTick = Infinity;
  let maxTick = 0;
  historial.forEach((c) => {
    if (typeof c.llegada === "number") minTick = Math.min(minTick, c.llegada);
    if (typeof c.inicio === "number") minTick = Math.min(minTick, c.inicio);
    if (typeof c.fin === "number") maxTick = Math.max(maxTick, c.fin);
    if (typeof c.llegada === "number") maxTick = Math.max(maxTick, c.llegada);
  });
  if (!isFinite(minTick)) minTick = 0;
  if (maxTick <= 0) maxTick = minTick + 10;

  const lanes = ["A", "M", "B"];
  const laneBaseY = 40;
  const laneHeight = 48;
  const rectHeight = 12;
  const rowGap = 4;

  const ticksRange = Math.max(1, maxTick - minTick + 1);
  const maxWidth = 1000;
  const pxPerTick = Math.max(
    3,
    Math.min(12, Math.floor(maxWidth / ticksRange))
  );
  const svgWidth = Math.min(maxWidth, ticksRange * pxPerTick + 160);

  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("width", String(svgWidth));
  svg.setAttribute("height", String(lanes.length * laneHeight + 120));
  svg.setAttribute(
    "viewBox",
    `0 0 ${svgWidth} ${lanes.length * laneHeight + 120}`
  );
  svg.setAttribute("style", "background:#fff; border:1px solid #eee;");

  const title = document.createElementNS(svgNS, "text");
  title.setAttribute("x", 10);
  title.setAttribute("y", 16);
  title.setAttribute("font-size", "13");
  title.setAttribute("fill", "#000");
  title.textContent =
    "Movimiento de clientes por tipo (espera = claro, servicio = oscuro)";
  svg.appendChild(title);

  const axisY = lanes.length * laneHeight + 50;
  const ticksToShow = Math.min(ticksRange, 20);
  const tickStep = Math.max(1, Math.ceil(ticksRange / ticksToShow));
  for (let t = minTick; t <= maxTick; t += tickStep) {
    const x = 120 + (t - minTick) * pxPerTick;
    const tickLine = document.createElementNS(svgNS, "line");
    tickLine.setAttribute("x1", x);
    tickLine.setAttribute("x2", x);
    tickLine.setAttribute("y1", 28);
    tickLine.setAttribute("y2", axisY + 6);
    tickLine.setAttribute("stroke", "#f0f0f0");
    tickLine.setAttribute("stroke-width", "1");
    svg.appendChild(tickLine);

    const tickText = document.createElementNS(svgNS, "text");
    tickText.setAttribute("x", x - 6);
    tickText.setAttribute("y", axisY + 22);
    tickText.setAttribute("font-size", "10");
    tickText.setAttribute("fill", "#333");
    tickText.textContent = String(t);
    svg.appendChild(tickText);
  }

  // Etiqueta del eje X (explicación de los números)
  const axisLabel = document.createElementNS(svgNS, "text");
  axisLabel.setAttribute("x", 120);
  axisLabel.setAttribute("y", axisY + 42);
  axisLabel.setAttribute("font-size", "11");
  axisLabel.setAttribute("fill", "#333");
  axisLabel.textContent = "Ticks (unidad de tiempo)";
  svg.appendChild(axisLabel);

  const laneRows = { A: [], M: [], B: [] };
  const maxRowsPerLane = 8;
  const items = historial
    .slice()
    .sort((a, b) => (a.llegada || 0) - (b.llegada || 0));
  function placeInRow(lane, x1, x2) {
    const rows = laneRows[lane];
    for (let r = 0; r < rows.length; r++) {
      const row = rows[r];
      let ok = true;
      for (let k = 0; k < row.length; k++) {
        if (intervalsOverlap(x1, x2, row[k][0], row[k][1])) {
          ok = false;
          break;
        }
      }
      if (ok) {
        row.push([x1, x2]);
        return r;
      }
    }
    if (rows.length < maxRowsPerLane) {
      rows.push([[x1, x2]]);
      return rows.length - 1;
    }
    rows[0].push([x1, x2]);
    return 0;
  }

  const tooltip = getTooltip();

  lanes.forEach((lane, idx) => {
    const y = laneBaseY + idx * laneHeight;
    const label = document.createElementNS(svgNS, "text");
    label.setAttribute("x", 10);
    label.setAttribute("y", y + 8);
    label.setAttribute("font-size", "12");
    label.setAttribute("fill", "#000");
    label.textContent = `Ventanilla ${lane}`;
    svg.appendChild(label);

    const line = document.createElementNS(svgNS, "line");
    line.setAttribute("x1", 120);
    line.setAttribute("x2", svgWidth - 10);
    line.setAttribute("y1", y + 8);
    line.setAttribute("y2", y + 8);
    line.setAttribute("stroke", "#eee");
    line.setAttribute("stroke-width", "1");
    svg.appendChild(line);
  });

  items.forEach((c) => {
    const lane = c.tipo;
    if (!lanes.includes(lane)) return;
    const llegada = typeof c.llegada === "number" ? c.llegada : null;
    const inicio = typeof c.inicio === "number" ? c.inicio : null;
    const fin = typeof c.fin === "number" ? c.fin : null;

    const waitStartTick =
      llegada !== null ? llegada : inicio !== null ? inicio : 0;
    const waitEndTick =
      inicio !== null ? inicio : fin !== null ? fin : waitStartTick + 1;
    const servStartTick = inicio !== null ? inicio : null;
    const servEndTick = fin !== null ? fin : null;

    const waitX = 120 + (waitStartTick - minTick) * pxPerTick;
    const waitW = Math.max(
      2,
      (waitEndTick - waitStartTick) * pxPerTick || pxPerTick
    );
    const servX =
      servStartTick !== null
        ? 120 + (servStartTick - minTick) * pxPerTick
        : null;
    const servW =
      servStartTick !== null && servEndTick !== null
        ? Math.max(2, (servEndTick - servStartTick) * pxPerTick)
        : 0;

    const x1 = waitX;
    const x2 =
      servX !== null && servW > 0
        ? Math.max(waitX + waitW, servX + servW)
        : waitX + waitW;
    const rowIndex = placeInRow(lane, x1, x2);

    const laneIdx = lanes.indexOf(lane);
    const baseY = laneBaseY + laneIdx * laneHeight;
    const y = baseY + 18 + rowIndex * (rectHeight + rowGap);

    const waitRect = document.createElementNS(svgNS, "rect");
    waitRect.setAttribute("x", String(waitX));
    waitRect.setAttribute("y", String(y));
    waitRect.setAttribute("width", String(waitW));
    waitRect.setAttribute("height", String(rectHeight));
    waitRect.setAttribute("fill", "#e6f2ff");
    waitRect.setAttribute("stroke", "#9ec5ff");
    waitRect.setAttribute("stroke-width", "0.4");
    svg.appendChild(waitRect);

    if (servW > 0 && servX !== null) {
      const servRect = document.createElementNS(svgNS, "rect");
      servRect.setAttribute("x", String(servX));
      servRect.setAttribute("y", String(y));
      servRect.setAttribute("width", String(servW));
      servRect.setAttribute("height", String(rectHeight));
      servRect.setAttribute("fill", "#1f78c1");
      servRect.setAttribute("stroke", "#0f4f86");
      servRect.setAttribute("stroke-width", "0.4");
      svg.appendChild(servRect);
      servRect.addEventListener("mousemove", (ev) => {
        const tip = getTooltip();
        tip.style.display = "block";
        tip.textContent = `${c.id} — tipo ${c.tipo}\ninicio: ${c.inicio} fin: ${c.fin}`;
        const rect = vizContainer.getBoundingClientRect();
        tip.style.left = ev.clientX - rect.left + 12 + "px";
        tip.style.top = ev.clientY - rect.top + 12 + "px";
      });
      servRect.addEventListener(
        "mouseleave",
        () => (getTooltip().style.display = "none")
      );
    }

    const labelX = servX !== null ? servX + 4 : waitX + 4;
    const text = document.createElementNS(svgNS, "text");
    text.setAttribute("x", String(labelX));
    text.setAttribute("y", String(y + rectHeight - 1));
    text.setAttribute("font-size", "10");
    text.setAttribute("fill", "#000");
    text.textContent = c.id;
    svg.appendChild(text);

    waitRect.addEventListener("mousemove", (ev) => {
      const tip = getTooltip();
      tip.style.display = "block";
      tip.textContent = `${c.id} — tipo ${c.tipo}\nllegada: ${c.llegada}${
        inicio !== null ? `\ninicio: ${inicio}` : ""
      }${fin !== null ? `\nfin: ${fin}` : ""}`;
      const rect = vizContainer.getBoundingClientRect();
      tip.style.left = ev.clientX - rect.left + 12 + "px";
      tip.style.top = ev.clientY - rect.top + 12 + "px";
    });
    waitRect.addEventListener(
      "mouseleave",
      () => (getTooltip().style.display = "none")
    );
  });

  const legendX = svgWidth - 220;
  const legendY = 30;
  const legendWait = document.createElementNS(svgNS, "rect");
  legendWait.setAttribute("x", legendX);
  legendWait.setAttribute("y", legendY);
  legendWait.setAttribute("width", "12");
  legendWait.setAttribute("height", "12");
  legendWait.setAttribute("fill", "#e6f2ff");
  legendWait.setAttribute("stroke", "#9ec5ff");
  svg.appendChild(legendWait);
  const legendWaitText = document.createElementNS(svgNS, "text");
  legendWaitText.setAttribute("x", legendX + 18);
  legendWaitText.setAttribute("y", legendY + 10);
  legendWaitText.setAttribute("font-size", "11");
  legendWaitText.textContent = "Espera en cola";
  svg.appendChild(legendWaitText);

  const legendServ = document.createElementNS(svgNS, "rect");
  legendServ.setAttribute("x", legendX);
  legendServ.setAttribute("y", legendY + 18);
  legendServ.setAttribute("width", "12");
  legendServ.setAttribute("height", "12");
  legendServ.setAttribute("fill", "#1f78c1");
  legendServ.setAttribute("stroke", "#0f4f86");
  svg.appendChild(legendServ);
  const legendServText = document.createElementNS(svgNS, "text");
  legendServText.setAttribute("x", legendX + 18);
  legendServText.setAttribute("y", legendY + 30);
  legendServText.setAttribute("font-size", "11");
  legendServText.textContent = "En servicio";
  svg.appendChild(legendServText);

  vizContainer.appendChild(svg);
}

// ---------------- Polling / control logic ----------------

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function waitForResult(intervalMs = 500) {
  showPreparing("Preparando ejecución...");
  show("Esperando resultado final...");
  while (true) {
    const res = await fetchJson("GET", "/simulacion/result", null);
    if (res.error) {
      hidePreparing();
      show("Error al obtener resultado: " + res.message);
      return;
    }
    if (res.status === 202) {
      const st = await fetchJson("GET", "/simulacion/status", null);
      if (!st.error) {
        showPreparing(
          `Simulación en ejecución — cola: ${st.body.cola_tamaño}, eventos: ${st.body.logs_count}`
        );
        show(humanize("/simulacion/status", st));
      } else {
        showPreparing("Simulación en ejecución...");
      }
      await sleep(intervalMs);
      continue;
    } else {
      hidePreparing();
      displayResponseFor("/simulacion/result", res);
      return;
    }
  }
}

async function startSim() {
  show("Iniciando petición de inicio...");
  const tiempoVal = el("tiempo") ? el("tiempo").value.trim() : "";
  const probLlegadaObj = buildProbObject("prob_llegada");
  if (probLlegadaObj && probLlegadaObj.error) {
    show("Validación: " + probLlegadaObj.error);
    return;
  }
  const probServicioObj = buildProbObject("prob_servicio");
  if (probServicioObj && probServicioObj.error) {
    show("Validación: " + probServicioObj.error);
    return;
  }

  const body = {};
  if (tiempoVal !== "") body.tiempo = Number(tiempoVal);
  if (probLlegadaObj !== null) body.prob_llegada = probLlegadaObj;
  if (probServicioObj !== null) body.prob_servicio = probServicioObj;

  const validation = validateInputs(
    body.tiempo ?? null,
    body.prob_llegada ?? null,
    body.prob_servicio ?? null
  );
  if (!validation.ok) {
    show("Validación: " + validation.message);
    return;
  }

  const btn = el("btnStart");
  if (btn) btn.disabled = true;
  const res = await fetchJson(
    "POST",
    "/simulacion/start",
    Object.keys(body).length ? body : null
  );
  if (btn) btn.disabled = false;

  show(humanize("/simulacion/start", res));

  if (res.status === 201 || res.ok) {
    await waitForResult(500);
  }
}

async function pauseSim() {
  const res = await fetchJson("POST", "/simulacion/pause", {});
  show(humanize("/simulacion/pause", res));
}
async function resumeSim() {
  const res = await fetchJson("POST", "/simulacion/resume", {});
  show(humanize("/simulacion/resume", res));
}
async function stopSim() {
  const res = await fetchJson("POST", "/simulacion/stop", {});
  show(humanize("/simulacion/stop", res));
}
async function restoreSim() {
  const res = await fetchJson("POST", "/simulacion/restore", {});
  show(humanize("/simulacion/restore", res));
}
async function statusSim() {
  const res = await fetchJson("GET", "/simulacion/status", null);
  show(humanize("/simulacion/status", res));
}
// note: removed resultSim and the btnResult binding to avoid exposing raw JSON

function bindListeners() {
  try {
    el("btnStart")?.addEventListener("click", startSim);
    el("btnPause")?.addEventListener("click", pauseSim);
    el("btnResume")?.addEventListener("click", resumeSim);
    el("btnStop")?.addEventListener("click", stopSim);
    el("btnRestore")?.addEventListener("click", restoreSim);
    el("btnStatus")?.addEventListener("click", statusSim);
    console.log("[main.js] listeners attached");
  } catch (err) {
    console.error("[main.js] bindListeners error:", err);
  }
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", bindListeners);
} else {
  bindListeners();
}
