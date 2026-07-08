# Project Structure

```
curio/
├── app/                          # Main application package
│   ├── server.py                 # Flask app entry point and all routes
│   ├── db.py                     # MongoDB / Beanie initialization
│   │
│   ├── auth/                     # Authentication layer
│   │   ├── auth_service.py       # Sign-up, login, avatar generation
│   │   └── session_key.py        # Session validation
│   │
│   ├── model/                    # Database document models
│   │   └── account.py            # Account, User, Sessions, Post
│   │
│   ├── post/                     # Post domain services
│   │   ├── all_posts.py          # User's own posts (paginated)
│   │   ├── explore_posts.py      # Public explore feed
│   │   ├── one_post.py           # Single post fetch + privacy check
│   │   └── edit_post.py          # View count, privacy toggle
│   │
│   ├── user/                     # User domain services
│   │   ├── get_user_account_info.py  # Profile by account_id
│   │   ├── get_username.py       # Profile and posts by username
│   │   └── edit_user.py          # Name, username, avatar, quota
│   │
│   ├── search/                   # Search services
│   │   └── search.py             # Profile and post search
│   │
│   ├── log/                      # Logging
│   │   └── log.py                # Logs model + log_now()
│   │
│   ├── stages/                   # AI content pipeline
│   │   ├── start_stage.py        # Pipeline orchestrator
│   │   ├── stage_1/              # Topic discovery (scrape)
│   │   ├── stage_2/              # Topic selection (LLM)
│   │   ├── stage_3/              # Research (search + scrape + clean)
│   │   ├── stage_4/              # Caption generation (LLM)
│   │   ├── stage_5/              # Image generation (LLM prompt + FLUX)
│   │   ├── stage_6/              # Image composition (PIL overlay)
│   │   └── stage_7/              # Save to DB + disk
│   │
│   ├── templates/                # Jinja2 HTML templates
│   │   ├── auth.html
│   │   ├── home.html
│   │   ├── post.html
│   │   ├── user.html
│   │   └── partials/
│   │       └── nav.html
│   │
│   ├── static/                   # CSS, JS, SVG assets
│   │   ├── auth.css / auth.js
│   │   ├── home.css / home.js
│   │   ├── post.css / post.js
│   │   ├── user.css / user.js
│   │   ├── nav.js
│   │   ├── post-notify.js
│   │   ├── post-notify-sw.js
│   │   └── assets/
│   │
│   └── assets/
│       └── profile/              # User avatar PNGs (gitignored)
│
├── data/
│   └── json/
│       ├── characters.json       # Meme character definitions
│       ├── used_topics.json      # Topics consumed by pipeline
│       └── latest_topics.json    # Daily scrape snapshots (runtime)
│
├── rage/
│   └── post/                     # Generated post PNGs (gitignored)
│
├── documentations/               # This documentation set
│
├── frontend/                     # Future React SPA (scaffold only)
│   ├── package.json
│   ├── vite.config.js
│   └── src/                      # Empty — not in production use
│
├── mongodb_local/                # Bundled MongoDB binaries (gitignored)
│
├── .env                          # Secrets (gitignored)
├── .env.example                  # Environment template
├── .gitignore
├── requirements.txt              # Python dependencies
└── README.md                     # Project overview
```

---

## Module Responsibilities

### Entry Point

| File | Role |
|------|------|
| `app/server.py` | Flask routes, cookie handling, page rendering, CORS |

Run with: `python -m app.server` from project root.

### Pipeline Stages

Each stage follows this pattern:

```
stage_N/
├── stage_N_man.py          # Orchestrator (called by start_stage.py)
└── <sub_task>/
    └── <implementation>.py # Single responsibility module
```

| Stage | Manager | Key modules |
|-------|---------|-------------|
| 1 | `stage_1_man.py` | `search_topic.py` |
| 2 | `stage_2_man.py` | `validate.py`, `choose.py`, `save.py` |
| 3 | `stage_3_man.py` | `research.py`, `scrap.py`, `clean_data.py` |
| 4 | `stage_4_man.py` | `meme.py` |
| 5 | `stage_5_man.py` | `meme_image_prompt.py`, `bg_image.py` |
| 6 | `stage_6_man.py` | `edit.py` |
| 7 | `stage_7_man.py` | `save.py` |

### Domain Services Pattern

Each service class follows a consistent return format:

```python
{
    "status": True | False,
    "data": { ... },
    "from": "ClassName.method_name"  # stripped by server.py before response
}
```

The `"from"` field is removed in route handlers via `.pop("from", None)`.

---

## Files Not in Git

See `.gitignore`:

- `.env`, `cookies.txt`
- `.venv/`, `__pycache__/`
- `mongodb_local/`
- `rage/post/*.png`
- `app/assets/profile/*.png`
- `data/json/latest_topics.json`
- `frontend/node_modules/`

---

## Naming Conventions

| Item | Convention | Example |
|------|------------|---------|
| Python modules | snake_case | `auth_service.py` |
| Classes | PascalCase | `AuthService` |
| API routes | snake_case paths | `/api/get_all_post` |
| MongoDB collections | lowercase plural | `accounts`, `users`, `posts` |
| Static assets | kebab or snake | `post-notify-sw.js` |
| Post images | `{object_id}.png` | `674a1b2c....png` |
| Avatars | `{email}.png` | `user@mail.com.png` |

---

## Import Path Note

Stage managers add the project root to `sys.path` for standalone execution compatibility:

```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
```

Always run the app from the **project root** so relative paths (`data/json/`, `rage/post/`) resolve correctly.

---

## Related Documents

- [Architecture](./02-architecture.md)
- [Getting Started](./03-getting-started.md)
- [Content Pipeline](./04-content-pipeline.md)
