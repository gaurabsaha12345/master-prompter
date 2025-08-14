## Prompt Enhancer

An expert prompt optimizer that transforms an initial idea into a clear, detailed, human-style prompt optimized for creativity, accuracy, and usability. It structures outputs to your selected Category/Purpose and applies best-practice prompt engineering.

### Features
- Category-aware prompt structures: Content Writing, Design, Code, Image Generation
- Optional role, sources/references, screenshot/image context, tone/style, and output requirements
- Adds guardrails, assumptions policy, and success criteria
- No dependencies; runs on any machine with Python 3.8+
- Advanced controls: Temperature, media resolution (low/medium/high), target model hint
- Model providers: choose from ChatGPT, Grok, Perplexity, Gemini, MiniMax
- API provides token estimate endpoint (heuristic or Gemini-powered if you extend it)

### Quick Start
```bash
python optimizer.py --category "Code" \
  --role "Act as a Python backend engineer" \
  --idea "Build a REST API for a Todo app with auth and tests" \
  --tone "technical" --tone "concise" \
  --output-length medium \
  --output-format "structured sections" \
  --extra "examples" --extra "tests" --extra "acceptance criteria" \
  --source "https://example.com/spec" \
  --out prompt.md
```

View the generated prompt in `prompt.md`.

### Inputs (CLI Flags)
- `--category` (required): One of `Content Writing`, `Design`, `Code`, `Image Generation`
- `--role` (optional): e.g., `Act as a senior copywriter`
- `--idea` (required): Your initial idea in plain words
- `--source` (repeatable): URLs, quotes, notes, datasets
- `--image` (optional): Screenshot/image description
- `--tone` (repeatable): e.g., `formal`, `witty`, `technical`
- `--output-length` (optional): `short`, `medium`, `long`
- `--output-format` (optional): e.g., `list`, `table`, `structured sections`, `plain text`
- `--extra` (repeatable): e.g., `examples`, `analogies`, `step-by-step`, `SEO`, `citations`
- `--out` (optional): File path to save the prompt; prints to stdout if omitted
- `--from` (optional): Load a JSON file containing all inputs (flags override file values)

Example JSON for `--from`:
```json
{
  "category": "Content Writing",
  "role": "Act as a senior copywriter",
  "idea": "Launch announcement blog post for our AI note-taking app",
  "sources": ["https://example.com/press-kit", "Key stats: 20k beta users"],
  "image": "App dashboard screenshot (clean, dark mode)",
  "tones": ["conversational", "persuasive"],
  "output_length": "long",
  "output_format": "structured sections",
  "extras": ["SEO", "examples"]
}
```

Run:
```bash
python optimizer.py --from input.json --out blog_prompt.md
```

### Full-Stack (Master Prompter)
Backend (FastAPI) and simple web UI are included.

1) Install deps (only for server/UI):
```bash
pip install fastapi uvicorn pydantic
```

2) Run API:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

3) Open UI:
Open `web/index.html` in your browser (the UI calls `http://localhost:8000`).

API endpoint: `POST /optimize`
```json
{
  "category": "Code",
  "idea": "Build a REST API for a Todo app with auth and tests",
  "role": "Act as a Python backend engineer",
  "sources": ["https://example.com/spec"],
  "image": null,
  "tones": ["technical", "concise"],
  "output_length": "medium",
  "output_format": "structured sections",
  "extras": ["examples", "tests", "acceptance criteria"],
  "temperature": 0.7,
  "media_resolution": "medium",
  "model": "gemini-1.5-pro",
  "provider": "Gemini"
}
```

Token estimate: `POST /tokens`
```json
{ "text": "...your prompt...", "model": "gemini-1.5-pro" }
```

Note: The default implementation uses a simple heuristic (1 token ≈ 4 characters). You can wire in Google Gemini token counting by adding your API key usage in `server.py`.

### Newsletter Subscription (SQLite)
- Endpoint: `POST /subscribe` with `{ "email": "you@example.com" }`
- Default DB: `newsletter.db` in project root (override with `DATABASE_URL`)

### Gemini Enhance Endpoint (Optional)
- Set env: `GOOGLE_API_KEY=...`
- Endpoint: `POST /enhance` with `{ "prompt": "...", "model": "gemini-1.5-pro", "temperature": 0.7 }`
- The UI includes an “Enhance with Gemini” button; errors will show if not configured.

### Deploying to GitHub Pages + API
- Host `web/` on GitHub Pages (static)
- Deploy API (FastAPI) on a host (Render/Fly/Heroku) and set CORS allowed origins accordingly.
- Optionally set UI API base in devtools: `localStorage.setItem('api_base','https://your-api.example.com')`

### Category Structures (Built-in)
- Content Writing: audience, objective, key messages, outline, voice, SEO guidance, fact-check boundaries
- Design: user persona, problem statement, platform/scope, constraints, deliverables, accessibility, branding, references, success criteria
- Code: stack/language, acceptance criteria, interfaces, tests, edge cases, non-functionals, error handling, security, performance targets
- Image Generation: subject, style, composition, camera/lighting, materials, render engine, aspect ratio, quality params, negative prompts

### Notes
- The optimizer avoids chain-of-thought requests and asks for concise rationale only when appropriate.
- If information is missing, the generated prompt includes an assumptions policy and focuses on delivering usable output immediately.


