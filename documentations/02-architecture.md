# Architecture

## High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client (Browser)                        │
│  auth.html │ home.html │ user.html │ post.html │ Service Worker │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP / cookies (sid)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Flask Application (server.py)                │
│  Routes: /api/* (REST)  │  /auth, /home  │  /{username|post_id} │
└──────┬──────────────────────────────┬───────────────────────────┘
       │                              │
       ▼                              ▼
┌──────────────┐              ┌───────────────────┐
│  Auth Layer  │              │  Content Pipeline │
│ AuthService  │              │  start_stage.py   │
│ SessionKey   │              │  stage_1 … stage_7│
└──────┬───────┘              └─────────┬─────────┘
       │                                │
       ▼                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MongoDB (database: rage)                    │
│   accounts │ users │ sessions │ posts │ logs                     │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  rage/post/*.png │    │ app/assets/profile│    │ data/json/      │
│  (post images)   │    │ (user avatars)    │    │ (pipeline state)│
└──────────────────┘    └──────────────────┘    └─────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.12+, Flask (async route handlers) |
| **Database** | MongoDB 4.4+ with Beanie ODM |
| **Auth** | bcrypt password hashing, HTTP-only session cookies |
| **LLM** | OpenAI Python SDK (OpenAI-compatible endpoint) |
| **Image gen** | Self-hosted API endpoint (via `IMAGE_MODEL_BASE_URL`) |
| **Image edit** | Pillow (PIL) |
| **Scraping** | requests, BeautifulSoup4, DuckDuckGo (ddgs) |
| **Frontend** | Server-rendered Jinja2 templates + vanilla JavaScript |
| **Notifications** | Service Worker (`post-notify-sw.js`) |

> **Note:** A separate `frontend/` directory contains a Vite + React scaffold for future UI work. The production UI currently lives in `app/templates/` and `app/static/`.

---

## Application Layers

### 1. HTTP Layer — `app/server.py`

Single Flask application exposing:

- **REST API** under `/api/*`
- **Server-rendered pages** for auth, home, profiles, and posts
- **Static asset serving** for CSS, JS, SVG icons, and images
- **Dynamic routing** — `/<segment>` resolves to post or profile by pattern

CORS is enabled globally via `flask-cors`.

### 2. Authentication Layer — `app/auth/`

| Module | Responsibility |
|--------|----------------|
| `auth_service.py` | Sign-up (create account + user + avatar) or login |
| `session_key.py` | Validate session ObjectId and expiry |

Sessions expire after 30 days (`2592000` seconds). The `sid` cookie is `HttpOnly`, `SameSite=Lax`.

### 3. Domain Services — `app/post/`, `app/user/`, `app/search/`

Business logic separated from routes:

- **Post** — CRUD-style reads, view counting, privacy toggle
- **User** — Profile reads, name/username/avatar updates, quota
- **Search** — Regex-based profile and post search

### 4. Content Pipeline — `app/stages/`

Seven sequential stages orchestrated by `start_stage.py`. Each stage has a manager file (`stage_N_man.py`) that calls specialized sub-modules. See [Content Pipeline](./04-content-pipeline.md).

### 5. Data Layer — `app/model/` + `app/db.py`

Beanie document models registered at startup via `init_db()`. All API handlers call `await init_db()` before database operations.

### 6. Logging — `app/log/`

Structured error and event logs persisted to the `logs` MongoDB collection via `log_now()`.

---

## Request Flow Examples

### Authenticated API Request

```
Browser → GET /api/get_user_all_info
       → Cookie: sid=<session_object_id>
       → SessionKey.validate()
       → GetUser(account_id).get_user_all_info()
       → JSON response
```

### Post Creation (via Service Worker)

```
User clicks "Create Post"
       → post-notify.js → Service Worker message CREATE_POST
       → SW fetches POST /api/create_post (with sid cookie)
       → start_stages(account_id) runs stages 1–7
       → Post saved, PNG written
       → Browser notification "Your new post is ready"
       → Click → navigate to /{post_id}
```

### Dynamic Page Resolution

```
GET /coolname1234
       → Not a 24-char hex ObjectId
       → GetUsername("coolname1234")
       → Render user.html

GET /674a1b2c3d4e5f6789012345
       → Matches ObjectId pattern
       → OnePost.get_one_post()
       → Render post.html (or 404 if private/missing)
```

---

## File Storage

| Path | Content | Git tracked |
|------|---------|-------------|
| `rage/post/{post_id}.png` | Generated post images | No (`.gitignore`) |
| `app/assets/profile/{email}.png` | User avatars | No (`.gitignore`) |
| `data/json/used_topics.json` | Topics already used by pipeline | Yes (seed data) |
| `data/json/characters.json` | Meme character definitions | Yes |
| `data/json/latest_topics.json` | Daily scraped topic snapshot | No (runtime) |

---

## Database

MongoDB database name: **`rage`** (legacy internal name — unchanged to preserve compatibility).

Collections:

| Collection | Beanie Model | Purpose |
|------------|--------------|---------|
| `accounts` | `Account` | Email + hashed password |
| `users` | `User` | Profile, plan, quota |
| `sessions` | `Sessions` | Active login sessions |
| `posts` | `Post` | Generated content |
| `logs` | `Logs` | Application logs |

See [Data Models](./06-data-models.md) for field-level detail.

---

## Design Decisions

1. **Single auth endpoint** — Sign-up and login share `/api/auth_service`; duplicate email triggers login path.
2. **Cookie-based sessions** — No JWT; session ID stored as MongoDB ObjectId in HttpOnly cookie.
3. **Synchronous pipeline stages** — Stages 1–6 run synchronously inside the async route; only Stage 7 (DB save) is async.
4. **Server-rendered UI** — No SPA framework in production; fast to ship, SEO-friendly profile/post URLs.
5. **OpenAI-compatible API** — Provider-agnostic LLM integration via `BASE_URL` + `API_KEY`.

---

## Related Documents

- [Content Pipeline](./04-content-pipeline.md)
- [Data Models](./06-data-models.md)
- [Authentication & Sessions](./07-authentication-and-sessions.md)
