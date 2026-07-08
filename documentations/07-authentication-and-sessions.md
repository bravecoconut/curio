# Authentication & Sessions

CURIO uses **email + password authentication** with **server-side sessions** stored in MongoDB. There is no separate sign-up endpoint — a single route handles both registration and login.

---

## Auth Flow

```
POST /api/auth_service { email, password }
        │
        ├── Email NOT in accounts → Create Account + User + Avatar + Session
        │
        └── Email EXISTS → Verify password → Create new Session
                │
                ▼
        Set HttpOnly cookie: sid=<session_object_id>
                │
                ▼
        Redirect to /home (via frontend)
```

---

## Sign Up

When a new email is submitted:

1. **Account** created with bcrypt-hashed password.
2. **User** profile created with:
   - Random username (`coolname` slug + 4-digit suffix)
   - Display name from email local part
   - Auto-generated identicon avatar (pydenticon → PNG in `app/assets/profile/`)
3. **Session** created with 30-day expiry.
4. **`sid` cookie** set on response.

Username collisions are retried in a loop until a unique username is found.

---

## Login

When an existing email is submitted:

1. Account looked up by email.
2. Password verified with `bcrypt.checkpw()`.
3. New session created (multiple concurrent sessions allowed).
4. **`sid` cookie** set on response.

**Wrong password:** `400` with `{ "error": "wrong credentials" }`.

---

## Session Cookie

| Property | Value |
|----------|-------|
| Name | `sid` |
| Value | MongoDB ObjectId of `Sessions` document |
| HttpOnly | `true` — not accessible to JavaScript |
| Secure | `false` in dev (set `true` for HTTPS production) |
| SameSite | `Lax` |
| Max-Age | `2592000` (30 days) |

Set in `app/server.py` → `auth_service()` route.

---

## Session Validation

Every protected endpoint:

1. Reads `request.cookies.get("sid")`.
2. Calls `SessionKey(session_key=sid).validate()`.
3. On success, extracts `account_id` from response.
4. On failure, returns `401`.

Validation checks:

- Session document exists
- `expiry_date >= current timestamp`

---

## Logout

```
GET /logout
```

Deletes the `sid` cookie and redirects to `/`.

**Note:** This only clears the browser cookie. The session document remains in MongoDB until expiry. There is no server-side session revocation endpoint.

---

## Page-Level Auth Guards

| Route | Behavior |
|-------|----------|
| `/` | Redirect to `/auth` |
| `/auth` | If valid session → redirect to `/home`; else show login |
| `/home` | Requires valid session; else redirect to `/auth` |
| `/{username}` | Public (no auth required) |
| `/{post_id}` | Public (private posts hidden unless owner) |

---

## Password Security

- Passwords hashed with **bcrypt** (`bcrypt.gensalt()` + `bcrypt.hashpw()`).
- Plaintext passwords never stored.
- No password reset flow implemented yet.

---

## Avatar Generation

On sign-up, `AuthService` generates a **pydenticon** identicon:

- 10×10 grid, 200×200px
- Foreground colors: `#651FFF`, `#00E676`, `#FF3D00`, `#00B0FF`
- Composited onto 256×256 canvas with 60% padding
- Saved as `app/assets/profile/{email}.png`

Users can replace avatars via `POST /api/change_profile_image`.

---

## Security Considerations for Production

| Item | Dev setting | Production recommendation |
|------|-------------|------------------------|
| `secure` cookie flag | `False` | Set `True` (HTTPS only) |
| `SameSite` | `Lax` | Keep `Lax` or use `Strict` |
| CORS | Enabled globally | Restrict to your domain |
| Rate limiting | None | Add rate limits on auth and create_post |
| Session cleanup | None | Cron job to delete expired sessions |
| Password reset | Not implemented | Add email verification flow |

---

## Frontend Auth Implementation

**File:** `app/static/auth.js`

- POST to `/api/auth_service` with `credentials: "include"`
- On success, redirects to `/home`
- Error modal auto-dismisses after 4 seconds

---

## Related Documents

- [API Reference](./05-api-reference.md) — `POST /api/auth_service`
- [Data Models](./06-data-models.md) — Account, User, Sessions schemas
- [Deployment](./11-deployment.md) — HTTPS cookie settings
