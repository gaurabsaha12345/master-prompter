const API_BASE = localStorage.getItem("api_base") || "http://localhost:8000";

async function generatePrompt(payload) {
  const res = await fetch(`${API_BASE}/optimize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Request failed");
  }
  return res.json();
}

async function countTokens(payload) {
  const res = await fetch(`${API_BASE}/tokens`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) return null;
  try { return await res.json(); } catch { return null; }
}

async function subscribe(email) {
  const res = await fetch(`${API_BASE}/subscribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function enhanceWithGemini(text, model, temperature) {
  const res = await fetch(`${API_BASE}/enhance`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: text, model, temperature }),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function parseCSV(text) {
  if (!text) return [];
  return text
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

document.getElementById("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const payload = {
    category: form.category.value,
    role: form.role.value || null,
    idea: form.idea.value,
    sources: parseCSV(form.sources.value),
    image: form.image.value || null,
    tones: parseCSV(form.tones.value),
    output_length: form.output_length.value || null,
    output_format: form.output_format.value || null,
    extras: parseCSV(form.extras.value),
    temperature: form.temperature.value ? Number(form.temperature.value) : null,
    media_resolution: form.media_resolution.value || null,
    model: form.model.value || null,
    provider: form.provider.value || null,
  };

  const output = document.getElementById("output");
  output.value = "Generating...";
  try {
    const data = await generatePrompt(payload);
    output.value = data.prompt;
  } catch (err) {
    output.value = `Error: ${err.message}`;
  }

  try {
    const t = await countTokens({ text: output.value, model: payload.model || undefined });
    if (t && typeof t.tokens === "number") {
      document.getElementById("tokens").value = String(t.tokens);
    }
  } catch (_) {}
});

document.getElementById("newsletter").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("email").value;
  const statusEl = document.getElementById("status");
  statusEl.textContent = "Submitting...";
  try {
    const data = await subscribe(email);
    statusEl.textContent = data.status === "already_subscribed" ? "Already subscribed" : "Subscribed!";
  } catch (err) {
    statusEl.textContent = "Error subscribing";
  }
});

document.getElementById("enhance").addEventListener("click", async () => {
  const output = document.getElementById("output");
  const form = document.getElementById("form");
  const model = form.model.value || "gemini-1.5-pro";
  const temperature = form.temperature.value ? Number(form.temperature.value) : undefined;
  try {
    const data = await enhanceWithGemini(output.value, model, temperature);
    output.value = data.enhanced;
  } catch (err) {
    alert("Enhance failed. Configure GOOGLE_API_KEY on the server.");
  }
});


