# Getting Started

This guide walks you through running CURIO locally from a fresh clone.

---

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.12+ | Async/await used throughout |
| MongoDB | 4.4+ | Must be running on `localhost:27017` |
| Git | Any recent | For cloning the repository |
| DejaVu Sans Bold | System font | Used for caption overlay (`/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`) |

### API Keys Required

| Variable | Service | Purpose |
|----------|---------|---------|
| `BASE_URL` | OpenAI-compatible LLM | Topic selection, captions, research |
| `API_KEY` | Same provider | Authentication |
| `RESONNING_MODEL` | Same provider | Model name for chat completions |
| `IMAGE_MODEL_BASE_URL` | Self-hosted API | Image generation endpoint |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-org/curio.git
cd curio
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your API credentials:

```env
BASE_URL=https://your-llm-provider.example.com
API_KEY=sk-your-key
RESONNING_MODEL=your-model-name
IMAGE_MODEL_BASE_URL=http://localhost:5000/generate
```

### 5. Start MongoDB

If MongoDB is not already running:

```bash
# Using system MongoDB
sudo systemctl start mongod

# Or using the bundled local copy (if present in mongodb_local/)
# See mongodb_local/ — not recommended for production; use a proper install
```

Verify connectivity:

```bash
mongosh --eval "db.runCommand({ ping: 1 })"
```

### 6. Ensure required directories exist

These are created automatically on first run, but you can pre-create them:

```bash
mkdir -p rage/post app/assets/profile data/json
```

Seed files `data/json/characters.json` and `data/json/used_topics.json` are included in the repo.

### 7. Run the application

From the **project root** (not inside `app/`):

```bash
python -m app.server
```

The server starts at **http://localhost:5000**.

---

## First Use

1. Open **http://localhost:5000** — you will be redirected to `/auth`.
2. Enter any email and password and click **Continue**.
   - New email → account created automatically with a generated username and identicon avatar.
   - Existing email → login with the same password.
3. After auth, you land on **http://localhost:5000/home** (explore feed).
4. Click your profile avatar in the nav → go to your profile page.
5. Click **create new post** to run the full AI pipeline.
   - Allow browser notifications when prompted (optional but recommended).
   - Pipeline takes 1–3 minutes depending on API latency.
6. When complete, view your post at `http://localhost:5000/{post_id}`.

---

## Verifying the Setup

### Check API health (after signing in via browser)

```bash
# Sign in through the UI first, then:
curl -b cookies.txt http://localhost:5000/api/get_user_all_info
```

### Check MongoDB collections

```bash
mongosh rage --eval "db.users.countDocuments()"
mongosh rage --eval "db.posts.countDocuments()"
```

---

## Common Issues

### `Connection refused` on MongoDB

Ensure MongoDB is running on port 27017. The app connects to `mongodb://localhost:27017` with database name `rage`.

### Font not found (Stage 6)

Install DejaVu fonts:

```bash
# Debian/Ubuntu
sudo apt install fonts-dejavu-core
```

### LLM API errors (Stages 2, 3, 4, 5)

Verify `BASE_URL`, `API_KEY`, and `RESONNING_MODEL` in `.env`. The URL must expose an OpenAI-compatible `/v1/chat/completions` endpoint.

### Image generation fails (Stage 5)

Ensure `IMAGE_MODEL_BASE_URL` points to a running image generation API that meets the specification in [Image Generation API](./13-image-generation-api.md). Test the endpoint with curl:

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test", "format": "json"}'
```

### Empty explore feed

The feed shows public posts from all users. Create a post and ensure `post_private` is `false` (default).

### Pipeline returns "stage 2 failed"

Usually means no unused topics remain. Clear or trim `data/json/used_topics.json`, or wait for new daily facts on thefactsite.com.

---

## Development Tips

- **Debug mode** is enabled in `server.py` (`debug=True`). Disable for production.
- **Pipeline logs** print stage numbers (`1` through `7`) to stdout during post creation.
- **Hot reload** — Flask debug mode restarts on file changes.

---

## Next Steps

- [Content Pipeline](./04-content-pipeline.md) — Understand each stage
- [API Reference](./05-api-reference.md) — Integrate programmatically
- [Image Generation API](./13-image-generation-api.md) — Set up image generation
- [Deployment](./11-deployment.md) — Ship to production
