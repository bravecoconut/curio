# SaaS Features

This document describes the multi-user SaaS capabilities that distinguish CURIO from its original local post-creation pipeline.

---

## Evolution: Local Pipeline → SaaS Platform

| Aspect | Original (local) | CURIO (SaaS) |
|--------|------------------|--------------|
| Users | Single operator | Multi-user with accounts |
| Auth | None | Email/password + sessions |
| Storage | Local files only | MongoDB + file storage |
| UI | Basic local UI | Full web app with profiles |
| Content feed | N/A | Global explore feed |
| Sharing | N/A | Public URLs for posts and profiles |
| Privacy | N/A | Per-post private toggle |
| Search | N/A | User and post search |
| Quotas | N/A | Per-plan usage limits |
| Notifications | N/A | Service worker background jobs |

---

## Multi-User Accounts

Every user gets:

- **Account** — Email + hashed password
- **Profile** — Username, display name, avatar, plan
- **Session** — 30-day login cookie
- **Posts** — Owned content linked by `account_id`

Usernames are auto-generated on sign-up and can be customized. Profile URLs are human-readable: `curio.example.com/{username}`.

---

## Usage Quotas

Free-tier users start with:

```
quota_used: 0
quota_limit: 5
user_plan: "free"
```

The frontend increments quota after successful post creation via `POST /api/increment_quota`. When `quota_used >= quota_limit`, further increments are rejected.

Plans (`free`, `basic`, `pro`) are stored on the user document. Plan upgrade logic is not yet implemented — the field exists for future billing integration.

---

## Explore Feed

The home page (`/home`) shows a **global feed** of public posts from all users:

- Sorted by `date_created` descending (newest first)
- Infinite scroll pagination
- Only posts with `post_private=false` and `post_blocked=false`
- Metadata panel shows author, views, fact, and research

This transforms CURIO from a personal tool into a **content discovery platform**.

---

## User Profiles

Public profile pages at `/{username}`:

- Avatar and display name
- Paginated post grid
- Share profile link
- Own profile: create post, logout, see private posts

Profile data is fetched via `GET /api/user/<username>` and posts via `GET /api/user/<username>/posts`.

---

## Post Sharing

Each post has a direct URL: `/{post_id}`

Features:

- Full image, fact, and research display
- View count tracking
- Copy link button
- Author profile link

Post images are served at `/api/post_image/{post_id}`.

---

## Privacy Controls

Post owners can toggle visibility:

```
GET /api/toggle_private/{post_id}
```

| State | Owner sees | Others see |
|-------|------------|------------|
| `post_private=false` | Yes | Yes (in explore + profile) |
| `post_private=true` | Yes | 404 / "private or does not exist" |

Private posts still appear on the owner's own profile grid.

---

## Search

Authenticated users can search from the nav bar:

| Mode | Endpoint | Matches |
|------|----------|---------|
| Users | `POST /api/search/profiles` | Username (partial, case-insensitive) |
| Posts | `POST /api/search/posts` | `post_fact` or `post_research` text |

Results open in a modal overlay. Toggle switches between user and post results.

---

## Background Post Creation

The service worker pattern allows users to:

1. Start post creation from their profile
2. Navigate away or switch tabs
3. Receive a browser notification when the post is ready
4. Click notification to view the new post

This is essential for SaaS UX because the pipeline takes 1–3 minutes.

---

## Content Moderation Hooks

The data model includes moderation fields ready for future admin tooling:

| Field | Model | Purpose |
|-------|-------|---------|
| `post_blocked` | Post | Hide post from all public views |
| `user_blocked` | User | Block user account |
| `user_warnings` | User | Track moderation warnings |

No admin UI exists yet, but fields can be set directly in MongoDB.

---

## Avatar System

- **Auto-generated** identicon on sign-up (unique per email)
- **User-uploaded** replacement via profile settings
- Served at `/api/profile_image/{account_id}`
- Cropped to square on upload

---

## Logging & Observability

All domain service errors are logged to the `logs` MongoDB collection:

```python
await log_now({
    "data": {"error": str(error)},
    "status": False,
    "from": "ClassName.method",
})
```

Useful for debugging production issues and building admin dashboards.

---

## Future SaaS Roadmap

Capabilities the architecture supports but are not yet implemented:

- [ ] Stripe/payment integration for plan upgrades
- [ ] Admin dashboard for moderation
- [ ] Email verification and password reset
- [ ] OAuth (Google, GitHub) sign-in
- [ ] Post likes and comments
- [ ] Follow/follower graph
- [ ] React SPA frontend (`frontend/` scaffold)
- [ ] Background job queue for post creation
- [ ] Cloud object storage for images
- [ ] CDN for post image delivery
- [ ] Rate limiting and abuse prevention

---

## Related Documents

- [Overview](./01-overview.md)
- [Data Models](./06-data-models.md)
- [Frontend & UI](./08-frontend-and-ui.md)
- [API Reference](./05-api-reference.md)
