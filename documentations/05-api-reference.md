# API Reference

**Base URL:** `http://localhost:5000`

All JSON API routes are prefixed with `/api`. Page routes (`/auth`, `/home`, `/{username}`, `/{post_id}`) are documented in [Frontend & UI](./08-frontend-and-ui.md).

---

## Response Format

Successful responses follow this shape:

```json
{
  "status": true,
  "data": { ... }
}
```

Error responses:

```json
{
  "status": false,
  "data": { "error": "description" }
}
```

Some unauthenticated routes return a flat `{ "error": "..." }` with an HTTP status code.

---

## Authentication

All authenticated endpoints require the **`sid`** HttpOnly cookie set by `POST /api/auth_service`.

---

## Endpoints

### Auth

#### `POST /api/auth_service`

Sign up or log in. Creates account on new email; validates password on existing email.

**Auth required:** No

**Request body:**

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

**Success (200):**

```json
{
  "status": true,
  "data": {
    "session_id": "674a1b2c3d4e5f6789012345"
  }
}
```

Sets cookie: `sid=<session_id>; HttpOnly; SameSite=Lax; Max-Age=2592000`

**Errors (400):**

```json
{ "data": { "error": "wrong credentials" }, "status": false }
```

---

### Posts

#### `POST /api/create_post`

Runs the full 7-stage AI pipeline and creates a new post for the authenticated user.

**Auth required:** Yes

**Request body:** None

**Success (200):**

```json
{
  "status": true,
  "data": {
    "new_post": "674a1b2c3d4e5f6789012345"
  }
}
```

**Errors:** `401` not authenticated, `400` pipeline failure

---

#### `GET /api/get_one_post/<post_id>`

Fetch a single post by MongoDB ObjectId. Increments view count on success.

**Auth required:** No (private posts require owner session)

**Success (200):**

```json
{
  "status": true,
  "data": {
    "post": {
      "id": "674a1b2c3d4e5f6789012345",
      "account_id": "...",
      "post_fact": "...",
      "post_research": "...",
      "post_views": 1,
      "post_shares": 0,
      "post_private": false,
      "post_blocked": false,
      "post_file_name": "674a1b2c3d4e5f6789012345.png",
      "date_created": 1710000000.0,
      "date_updated": 1710000000.0
    }
  }
}
```

**Errors:** `404` not found or private

---

#### `POST /api/get_all_post`

Paginated list of the authenticated user's own posts (includes private).

**Auth required:** Yes

**Request body (optional):**

```json
{
  "start": 1,
  "end": 10
}
```

Uses **1-indexed inclusive** range. `start=1, end=10` returns the first 10 posts.

**Success (200):**

```json
{
  "status": true,
  "data": {
    "posts": [ ... ],
    "count": 5,
    "range": { "start": 1, "end": 10 }
  }
}
```

---

#### `POST /api/get_explore_posts`

Paginated public feed across all users. Sorted by `date_created` descending.

**Auth required:** Yes

**Request body (optional):**

```json
{
  "start": 1,
  "end": 10
}
```

Only returns posts where `post_private=false` and `post_blocked=false`.

---

#### `GET /api/post_image/<filename>`

Serve the generated post PNG. `<filename>` is the post ObjectId (without extension).

**Auth required:** No

**Side effect:** Increments view count.

**Returns:** PNG image file, or `404` JSON error.

---

#### `GET /api/toggle_private/<post_id>`

Toggle `post_private` on a post owned by the authenticated user.

**Auth required:** Yes

**Success (200):**

```json
{
  "status": true,
  "data": {
    "post_private": true
  }
}
```

---

### User Profile (Authenticated)

#### `GET /api/get_user_all_info`

Full profile for the currently logged-in user.

**Auth required:** Yes

**Success (200):**

```json
{
  "status": true,
  "data": {
    "user": {
      "account_id": "...",
      "user_name": "john",
      "username": "coolname1234",
      "user_avatar": "user@example.com.png",
      "user_plan": "free",
      "quota_used": 1,
      "quota_limit": 5,
      "user_blocked": false,
      "user_warnings": 0,
      "date_created": 1710000000.0,
      "date_updated": 1710000000.0
    }
  }
}
```

---

#### `GET /api/get_user_username/<account_id>`

Look up a user by `account_id` (used internally by the feed UI).

**Auth required:** No

---

#### `POST /api/change_name`

Update display name (`user_name`).

**Auth required:** Yes

**Request body:**

```json
{
  "new_name": "John Doe"
}
```

---

#### `POST /api/change_username`

Update unique username. Enforced by unique index on `users.username`.

**Auth required:** Yes

**Request body:**

```json
{
  "new_username": "johndoe123"
}
```

**Error:** `400` if username already taken.

---

#### `POST /api/increment_quota`

Increment `quota_used` by 1. Fails if limit reached.

**Auth required:** Yes

**Success (200):**

```json
{
  "status": true,
  "data": {
    "quota_used": 2,
    "quota_limit": 5
  }
}
```

---

#### `POST /api/change_profile_image`

Upload a new avatar. Multipart form with field `image`.

**Auth required:** Yes

**Success (200):**

```json
{
  "status": true,
  "data": {
    "user_avatar": "user@example.com.png"
  }
}
```

Image is cropped to square and saved as `{email}.png`.

---

#### `GET /api/profile_image/<account_id>`

Serve user avatar PNG.

**Auth required:** No

**Errors:** `404` if user not found or avatar is `"later"` / unset.

---

### Public Profiles

#### `GET /api/user/<username>`

Public profile info by username.

**Auth required:** No

---

#### `GET /api/user/<username>/posts`

Paginated posts for a user profile.

**Auth required:** No (viewer session optional — affects private post visibility)

**Query params or JSON body:**

```json
{
  "start": 1,
  "end": 10
}
```

- **Owner viewing own profile:** returns all posts including private.
- **Other viewers:** only public, non-blocked posts.

---

### Search

#### `POST /api/search/profiles`

Search users by username (case-insensitive partial match).

**Auth required:** Yes

**Request body:**

```json
{
  "keyword": "john",
  "start": 1,
  "end": 10
}
```

**Success (200):**

```json
{
  "status": true,
  "data": {
    "users": [ ... ],
    "count": 3,
    "range": { "start": 1, "end": 10 }
  }
}
```

---

#### `POST /api/search/posts`

Search public posts by keyword in `post_fact` or `post_research`.

**Auth required:** Yes

**Request body:**

```json
{
  "keyword": "banana",
  "start": 1,
  "end": 10
}
```

---

## Service Worker Route

#### `GET /post-notify-sw.js`

Serves the post creation service worker with header `Service-Worker-Allowed: /`.

Not under `/api` — registered at site root scope.

---

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request / business logic failure |
| 401 | Missing or invalid session |
| 404 | Resource not found |

---

## Pagination Convention

All paginated endpoints use **1-indexed inclusive** ranges:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `start` | `1` | First item index (1-based) |
| `end` | `10` | Last item index (inclusive) |

Example: pages of 10 items — page 1: `start=1, end=10`, page 2: `start=11, end=20`.

---

## Related Documents

- [Authentication & Sessions](./07-authentication-and-sessions.md)
- [Data Models](./06-data-models.md)
- [Frontend & UI](./08-frontend-and-ui.md)
