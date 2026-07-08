# Frontend & UI

CURIO's production user interface is built with **server-rendered Jinja2 templates** and **vanilla JavaScript**. 

---

## Page Map

| Route | Template | JS | CSS | Purpose |
|-------|----------|----|-----|---------|
| `/auth` | `auth.html` | `auth.js` | `auth.css` | Login / sign-up |
| `/home` | `home.html` | `home.js`, `nav.js`, `post-notify.js` | `home.css` | Explore feed |
| `/{username}` | `user.html` | `user.js`, `nav.js`, `post-notify.js` | `user.css`, `home.css` | User profile |
| `/{post_id}` | `post.html` | `post.js`, `nav.js`, `post-notify.js` | `post.css`, `home.css` | Post detail |

All authenticated pages include `partials/nav.html` for the top navigation bar.

---

## Navigation Bar

**Template:** `app/templates/partials/nav.html`  
**Script:** `app/static/nav.js`

Components:

- **Brand link** — CURIO logo/title → `/home`
- **Search input** — Live search with debounce
- **Search modal** — Toggle between user and post results
- **Profile avatar** — Loaded after `GET /api/get_user_all_info`; click → profile page

Search calls:
- `POST /api/search/profiles` (default)
- `POST /api/search/posts` (when toggled)

Nav hides on scroll down, reappears on scroll up.

---

## Auth Page

**URL:** `/auth`

- Email + password inputs
- **Continue** button triggers sign-up or login
- Enter key in password field submits
- Error modal for validation and API failures

---

## Home / Explore Feed

**URL:** `/home` (authenticated)

Layout:

```
┌─────────────────────────────────────┐
│  Nav (search + profile)             │
├──────────────────┬──────────────────┤
│  Post images     │  Post metadata   │
│  (scroll feed)   │  (sticky panel)  │
│                  │  - author        │
│                  │  - views, time   │
│                  │  - fact          │
│                  │  - research (MD) │
└──────────────────┴──────────────────┘
```

Features:

- **Infinite scroll** — IntersectionObserver loads more posts via `POST /api/get_explore_posts`
- **Active post tracking** — Visible post updates the metadata panel
- **Markdown rendering** — Research text rendered via `marked.js` CDN
- **Relative timestamps** — `Intl.RelativeTimeFormat`

---

## User Profile Page

**URL:** `/{username}`

Sections:

- **Profile header** — Avatar, username, display name
- **Actions** — Share link, logout (own profile), create new post (own profile)
- **Posts grid** — Paginated thumbnail grid with infinite scroll

Own profile extras:

- **Create new post** — Triggers service worker pipeline
- **Logout** — Navigates to `/logout`
- Shows private posts in grid

Other users' profiles show only public posts.

---

## Post Detail Page

**URL:** `/{post_id}` (24-char MongoDB ObjectId)

Displays:

- Full post image (`/api/post_image/{post_id}`)
- Author profile link
- View count and relative time
- Original fact text
- Research summary (Markdown)
- **Copy post link** button
- **Privacy toggle** (own posts only)

Private or missing posts show: *"this post is private or does not exist"*

---

## Post Creation UX

**Files:** `post-notify.js`, `post-notify-sw.js`

Flow:

1. User clicks **create new post** on profile page.
2. Browser requests notification permission.
3. Service worker registered at `/post-notify-sw.js`.
4. SW receives `CREATE_POST` message → calls `POST /api/create_post`.
5. On success:
   - Browser notification: *"Your new post is ready"*
   - Click notification → navigate to `/{post_id}`
6. Fallback (`fallbackCreatePost`) available if SW unavailable.

---

## Static Assets

```
app/static/
├── auth.css / auth.js
├── home.css / home.js
├── post.css / post.js
├── user.css / user.js
├── nav.js
├── post-notify.js
├── post-notify-sw.js
└── assets/
    ├── views.svg
    └── ago.svg
```

Profile images served from `/api/profile_image/{account_id}`.  
Post images served from `/api/post_image/{filename}`.

---

## Shared JavaScript Utilities

| Function | File | Purpose |
|----------|------|---------|
| `move_to_user_page(username)` | `nav.js` | Navigate to profile |
| `move_to_post_page(postId)` | `nav.js` | Navigate to post |
| `timeAgo(unixSeconds)` | `home.js`, `post.js`, `user.js` | Relative time display |
| `startCreatePost()` | `post-notify.js` | Background post creation |
| `populate_meta(index)` | `home.js` | Update feed metadata panel |

---

## Future Frontend (`frontend/`)

A **Vite + React 19** scaffold exists at `frontend/` but is **not wired to the backend** yet. It contains:

- `package.json` with React 19 and Vite 8
- Empty `src/` directory
- Default Vite config

This is reserved for a future SPA rewrite. The current production UI remains in `app/templates/` and `app/static/`.

---

## Styling Approach

- Custom CSS per page (no framework)
- Dark theme aesthetic
- Responsive layout with sticky metadata panel on desktop
- CSS classes: `.hidden` for toggle visibility

---

## Related Documents

- [API Reference](./05-api-reference.md)
- [SaaS Features](./12-saas-features.md)
- [Architecture](./02-architecture.md)
