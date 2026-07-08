# Overview

## What is CURIO?

**CURIO** (*Content Using Research & Intelligent Output*) is a SaaS platform that turns real-world facts into shareable, AI-generated meme posts. Users sign up, trigger a multi-stage content pipeline, and receive a finished image post with research-backed context — ready to publish or share.

What began as a local post-creation script with a basic UI has evolved into a full multi-user web application with authentication, profiles, an explore feed, search, quotas, and privacy controls.

---

## Core Value Proposition

| Capability | Description |
|------------|-------------|
| **Automated discovery** | Scrapes daily facts from curated sources |
| **Intelligent selection** | LLM picks the most meme-worthy topic from candidates |
| **Deep research** | Web search + scraping + AI summarization |
| **Creative output** | Character-driven captions and FLUX-generated imagery |
| **Social platform** | User profiles, explore feed, search, and shareable URLs |

---

## Platform Features

### For End Users

- **Unified auth** — Single endpoint handles sign-up and login; session cookie (`sid`) keeps you signed in for 30 days.
- **One-click post creation** — Trigger the full 7-stage pipeline from your profile page.
- **Background notifications** — Service worker runs post creation in the background and notifies when ready.
- **Explore feed** — Infinite-scroll feed of public posts from all users.
- **User profiles** — Public profile pages at `/{username}` with post grids.
- **Post pages** — Direct links at `/{post_id}` with fact, research, and image.
- **Privacy toggle** — Make posts private so only you can see them.
- **Search** — Find users by username or posts by keyword.
- **Profile customization** — Change display name, username, and avatar.
- **Usage quotas** — Free-tier post limits enforced per account.

### For Developers

- **Modular pipeline** — Seven independent stages, each with a manager (`stage_N_man.py`) orchestrating sub-tasks.
- **REST API** — JSON endpoints for all platform operations.
- **MongoDB + Beanie** — Async ODM with typed document models.
- **OpenAI-compatible LLM** — Works with any provider exposing an OpenAI-compatible API.
- **Hugging Face inference** — Image generation via `black-forest-labs/FLUX.1-schnell`.

---

## How a Post Is Created

```
User clicks "Create Post"
        │
        ▼
Stage 1  →  Scrape daily facts from thefactsite.com
Stage 2  →  Deduplicate, LLM-select best topic, mark as used
Stage 3  →  DuckDuckGo search → scrape sources → AI summarize
Stage 4  →  LLM writes meme caption (character + dark humor)
Stage 5  →  LLM image prompt → FLUX background image
Stage 6  →  PIL overlay: caption text + fade on image
Stage 7  →  Save to MongoDB + write PNG to rage/post/
        │
        ▼
User receives notification → views post at /{post_id}
```

See [Content Pipeline](./04-content-pipeline.md) for stage-by-stage detail.

---

## User Plans & Quotas

| Plan | Default quota limit | Notes |
|------|---------------------|-------|
| `free` | 5 posts | Assigned on sign-up |
| `basic` | Configurable | Stored on user document |
| `pro` | Configurable | Stored on user document |

Quota is tracked via `quota_used` / `quota_limit` on the `User` document. The frontend calls `/api/increment_quota` after a successful post creation.

---

## URL Routing

| URL pattern | Page |
|-------------|------|
| `/` | Redirects to `/auth` |
| `/auth` | Login / sign-up |
| `/home` | Explore feed (authenticated) |
| `/logout` | Clears session cookie |
| `/{username}` | Public user profile |
| `/{post_id}` | Post detail (24-char MongoDB ObjectId) |

---

## External Dependencies

| Service | Purpose |
|---------|---------|
| MongoDB | Primary database (`rage` database) |
| OpenAI-compatible LLM API | Topic selection, captions, research, prompts |
| Hugging Face Inference | FLUX.1-schnell image generation |
| DuckDuckGo | Web search for research |
| thefactsite.com | Daily fact scraping (Stage 1) |

---

## Related Documents

- [Architecture](./02-architecture.md) — Technical design
- [Getting Started](./03-getting-started.md) — Run locally
- [SaaS Features](./12-saas-features.md) — Multi-user platform capabilities
