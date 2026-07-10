# Configuration

All sensitive configuration is loaded from environment variables via `python-dotenv`.

---

## Environment Variables

Copy `.env.example` to `.env` in the project root.

| Variable | Required | Description |
|----------|----------|-------------|
| `BASE_URL` | Yes | Base URL of your OpenAI-compatible LLM provider (no trailing slash) |
| `API_KEY` | Yes | API key for the LLM provider |
| `RESONNING_MODEL` | Yes | Model name for chat completions |
| `IMAGE_MODEL_BASE_URL` | Yes | Self-hosted image generation API endpoint |

### Example `.env`

```env
BASE_URL=https://openrouter.ai/api
API_KEY=sk-or-v1-xxxxxxxx
RESONNING_MODEL=anthropic/claude-3.5-sonnet
IMAGE_MODEL_BASE_URL=http://localhost:5000/generate
```

---

## Where Variables Are Used

| Variable | Used in | Purpose |
|----------|---------|---------|
| `BASE_URL` | Stages 2, 3, 4, 5 | `OpenAI(base_url=f"{BASE_URL}/v1")` |
| `API_KEY` | Stages 2, 3, 4, 5 | LLM authentication |
| `RESONNING_MODEL` | Stages 2, 3, 4, 5 | Model identifier in `chat.completions.create()` |
| `IMAGE_MODEL_BASE_URL` | Stage 5 | Self-hosted image generation API endpoint |

All LLM stages call `load_dotenv()` at module import time.

---

## LLM Provider Requirements

The provider must expose an **OpenAI-compatible Chat Completions API**:

```
POST {BASE_URL}/v1/chat/completions
```

Stages and their LLM settings:

| Stage | Temperature | Task |
|-------|-------------|------|
| 2 — Topic selection | 0.2 | Deterministic index pick |
| 3 — Research clean | 0.2 | Factual summarization |
| 4 — Caption | 0.85 | Creative meme text |
| 5 — Image prompt | 0.8 | Scene description |

All stages use **streaming** completions.

---

## Image Generation API Configuration

CURIO requires a self-hosted image generation API endpoint. The API must accept POST requests with a JSON body containing a `prompt` field and return a JSON response with a base64-encoded image.

**Required API Specification:**

- **Endpoint:** Configured via `IMAGE_MODEL_BASE_URL`
- **Method:** POST
- **Request Body:** `{"prompt": "...", "format": "json"}`
- **Response:** `{"image_base64": "...", "seed": 123, "model": "..."}`

See [Image Generation API](./13-image-generation-api.md) for complete specification and reference implementation.

---

## MongoDB Configuration

Hardcoded in `app/db.py`:

```python
client = AsyncMongoClient("mongodb://localhost:27017")
database = client.rage
```

To use a remote MongoDB instance, update the connection string in `app/db.py` or externalize it to an environment variable (future improvement).

---

## Flask Server Configuration

In `app/server.py`:

```python
app.run(debug=True, port=5000, threaded=False)
```

| Setting | Dev value | Production note |
|---------|-----------|-----------------|
| `debug` | `True` | Set `False` |
| `port` | `5000` | Use reverse proxy |
| `threaded` | `False` | Use gunicorn/uvicorn workers |

---

## Cookie Configuration

In `app/server.py` → `auth_service()`:

```python
resp.set_cookie(
    "sid", session_id,
    httponly=True,
    secure=False,      # Set True behind HTTPS
    samesite="Lax",
    max_age=2592000,   # 30 days
)
```

---

## Font Dependency

Stage 6 requires **DejaVu Sans Bold**:

```
/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
```

Install on Debian/Ubuntu:

```bash
sudo apt install fonts-dejavu-core
```

---

## External Service URLs

| Service | URL | Configurable |
|---------|-----|--------------|
| Fact source | `https://www.thefactsite.com/daily-facts/` | Edit `search_topic.py` |
| DuckDuckGo | Via `ddgs` library | No config needed |
| LLM API | `{BASE_URL}/v1` | `.env` |
| Image Generation API | `{IMAGE_MODEL_BASE_URL}` | `.env` |

---

## Character Configuration

Edit `data/json/characters.json` to add or modify meme characters:

```json
[
  {
    "character": "Character Name",
    "trope": "Brief personality description for the LLM"
  }
]
```

Changes take effect on next pipeline run (no restart required if using file reload).

---

## Related Documents

- [Getting Started](./03-getting-started.md)
- [Content Pipeline](./04-content-pipeline.md)
- [Image Generation API](./13-image-generation-api.md)
- [Deployment](./11-deployment.md)
