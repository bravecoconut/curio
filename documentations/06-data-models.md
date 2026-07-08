# Data Models

CURIO uses **MongoDB** with **Beanie ODM** (Pydantic-based document models). All models are defined in `app/model/account.py` and registered in `app/db.py`.

**Database name:** `rage`  
**Connection:** `mongodb://localhost:27017`

---

## Collections Overview

| Collection | Model class | Description |
|------------|-------------|-------------|
| `accounts` | `Account` | Login credentials |
| `users` | `User` | Public profile and plan data |
| `sessions` | `Sessions` | Active login sessions |
| `posts` | `Post` | Generated content |
| `logs` | `Logs` | Application event logs |

---

## Account

Stores email and hashed password. One account maps to one user profile.

```python
class Account(Document):
    email: EmailStr          # Unique
    password: str            # bcrypt hash
    created_at: float
    password_updated_at: float
```

**Indexes:** Unique on `email`

**Notes:**
- Password hashed with `bcrypt.gensalt()` on sign-up.
- Login validates with `bcrypt.checkpw()`.

---

## User

Profile, plan, and quota information linked to an account.

```python
class User(Document):
    account_id: str          # References Account.id
    user_name: str           # Display name
    username: str            # Unique URL slug (@coolname1234)
    user_avatar: str         # Filename, e.g. "user@mail.com.png"
    user_plan: Literal["free", "basic", "pro"] = "free"
    quota_used: int = 0
    quota_limit: int = 5
    user_blocked: bool = False
    user_warnings: int = 0
    date_created: float
    date_updated: float
```

**Indexes:** Unique on `username`

**Sign-up defaults:**
- `user_name` — email local part (before `@`)
- `username` — `{coolname_slug}{4-digit random}` via `coolname` library
- `user_avatar` — auto-generated identicon saved to `app/assets/profile/{email}.png`

---

## Sessions

Login session tokens. The session ObjectId is stored in the `sid` cookie.

```python
class Sessions(Document):
    account_id: str
    logged_at: float
    ip_was: Optional[str] = None
    expiry_date: float       # Default: now + 30 days (2592000 seconds)
```

**Validation (`SessionKey.validate`):**
1. Lookup session by ObjectId.
2. Check `expiry_date >= time.time()`.
3. Return `account_id` on success.

---

## Post

Generated content from the AI pipeline.

```python
class Post(Document):
    account_id: str
    post_file_name: str = ""     # e.g. "{id}.png"
    post_fact: str               # Original fact / topic text
    post_research: str           # AI-summarized research paragraph
    post_views: int = 0
    post_shares: int = 0
    post_private: bool = False
    post_blocked: bool = False
    date_created: float
    date_updated: float
```

**Image storage:** `rage/post/{post.id}.png` on disk; `post_file_name` stores the filename.

**Visibility rules:**
- `post_private=true` → only owner can view via API or page
- `post_blocked=true` → hidden from all public queries (returns 404)

---

## Logs

Structured application logs for errors and events.

```python
class Logs(Document):
    data: dict
    status: bool
    from_source: str         # Alias: "from" in payload
    created: int
```

Written via `log_now()` in `app/log/log.py`.

---

## Entity Relationships

```
Account (1) ────── (1) User
    │
    └────── (N) Sessions
    │
    └────── (N) Post
```

- `User.account_id` → `Account.id` (stringified ObjectId)
- `Post.account_id` → `Account.id`
- `Sessions.account_id` → `Account.id`

There is no foreign key enforcement — relationships are maintained by application logic.

---

## JSON Pipeline Files

These are **not** MongoDB documents but file-based state for the content pipeline:

### `data/json/used_topics.json`

Array of topic objects already consumed by the pipeline:

```json
[
  {"topic": "Humans share 60% DNA with bananas."}
]
```

### `data/json/characters.json`

Meme character definitions for Stages 4 and 5:

```json
[
  {"character": "Homer Simpson", "trope": "lazy irony, relatable self-destruction"}
]
```

### `data/json/latest_topics.json`

Dated snapshots from Stage 1 scraping (runtime-generated):

```json
{
  "2026-07-09": [
    {"topic": "..."}
  ]
}
```

---

## Query Patterns

### Explore feed (public posts)

```python
Post.find(
    Post.post_private == False,
    Post.post_blocked == False,
).sort(-Post.date_created)
```

### User's own posts

```python
Post.find(Post.account_id == account_id).sort(-Post.date_created)
```

### Profile search

```python
User.find({"username": {"$regex": keyword, "$options": "i"}})
```

### Post search

```python
Post.find({
    "$and": [
        {"$or": [
            {"post_fact": {"$regex": keyword, "$options": "i"}},
            {"post_research": {"$regex": keyword, "$options": "i"}},
        ]},
        {"post_private": False},
        {"post_blocked": False},
    ]
})
```

---

## Related Documents

- [Architecture](./02-architecture.md)
- [API Reference](./05-api-reference.md)
- [SaaS Features](./12-saas-features.md)
