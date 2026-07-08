# Deployment

This guide covers deploying CURIO to a production environment.

---

## Production Checklist

- [ ] MongoDB running with authentication enabled
- [ ] Environment variables set (never commit `.env`)
- [ ] HTTPS enabled with valid TLS certificate
- [ ] Cookie `secure=True` in `server.py`
- [ ] Flask `debug=False`
- [ ] Process manager (gunicorn/systemd) configured
- [ ] Reverse proxy (nginx/Caddy) in front of Flask
- [ ] Font package installed (`fonts-dejavu-core`)
- [ ] Writable directories: `rage/post/`, `app/assets/profile/`
- [ ] API rate limiting on auth and create_post endpoints
- [ ] MongoDB backups scheduled

---

## Recommended Stack

```
Internet
    │
    ▼
┌─────────────┐
│  nginx/Caddy │  TLS termination, static caching
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  gunicorn    │  WSGI/ASGI workers
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Flask app   │  app.server:app
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MongoDB     │  Local or Atlas
└─────────────┘
```

---

## Process Manager (gunicorn)

Install:

```bash
pip install gunicorn
```

Run (from project root):

```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 "app.server:app"
```

**Note:** Post creation can take several minutes. Set `--timeout` high enough (300s+) to avoid worker kills mid-pipeline.

For async Flask routes, consider:

```bash
pip install gevent
gunicorn --worker-class gevent --bind 0.0.0.0:5000 --workers 2 --timeout 300 "app.server:app"
```

---

## Reverse Proxy (nginx)

```nginx
server {
    listen 443 ssl;
    server_name curio.example.com;

    ssl_certificate     /etc/ssl/certs/curio.crt;
    ssl_certificate_key /etc/ssl/private/curio.key;

    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    location /post-notify-sw.js {
        proxy_pass http://127.0.0.1:5000;
        add_header Service-Worker-Allowed /;
    }
}
```

---

## systemd Service

```ini
# /etc/systemd/system/curio.service
[Unit]
Description=CURIO SaaS Platform
After=network.target mongod.service

[Service]
User=curio
WorkingDirectory=/opt/curio
EnvironmentFile=/opt/curio/.env
ExecStart=/opt/curio/.venv/bin/gunicorn \
    --bind 127.0.0.1:5000 \
    --workers 2 \
    --timeout 300 \
    "app.server:app"
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable curio
sudo systemctl start curio
```

---

## MongoDB Production

### Option A: Self-hosted

Enable authentication:

```javascript
use admin
db.createUser({ user: "curioAdmin", pwd: "...", roles: ["root"] })
```

Update connection string in `app/db.py`:

```python
client = AsyncMongoClient("mongodb://curioAdmin:password@localhost:27017/rage?authSource=admin")
```

### Option B: MongoDB Atlas

1. Create a cluster on [MongoDB Atlas](https://www.mongodb.com/atlas).
2. Whitelist your server IP.
3. Use the connection string in `app/db.py`.

---

## HTTPS Cookie Settings

In `app/server.py`, update the cookie in `auth_service()`:

```python
resp.set_cookie(
    "sid", session_id,
    httponly=True,
    secure=True,        # Required for HTTPS
    samesite="Lax",
    max_age=2592000,
)
```

---

## Environment Variables in Production

Set via systemd `EnvironmentFile`, Docker secrets, or your cloud provider's secret manager. Never bake secrets into the image or repo.

```bash
# /opt/curio/.env
BASE_URL=https://your-llm-provider.example.com
API_KEY=sk-...
RESONNING_MODEL=your-model
HF_TOKEN=hf_...
```

---

## File Permissions

```bash
chown -R curio:curio /opt/curio
chmod 750 /opt/curio
chmod 700 /opt/curio/.env
mkdir -p /opt/curio/rage/post /opt/curio/app/assets/profile
chmod 770 /opt/curio/rage/post /opt/curio/app/assets/profile
```

---

## Docker (Optional)

Example Dockerfile outline:

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y fonts-dejavu-core && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .
RUN mkdir -p rage/post app/assets/profile

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "app.server:app"]
```

Run with MongoDB as a separate container or external service.

---

## Monitoring

- **Application logs** — gunicorn stdout + MongoDB `logs` collection
- **Pipeline failures** — Watch for `"stage 2 failed"` in stdout
- **Disk usage** — `rage/post/` grows with each generated post
- **API costs** — Monitor LLM and Hugging Face usage

---

## Scaling Considerations

| Bottleneck | Mitigation |
|------------|------------|
| Long post creation | Background job queue (Celery/RQ) — future improvement |
| Single-threaded pipeline | Queue workers per post |
| MongoDB writes | Replica set for HA |
| Image storage | Move to S3/Cloudflare R2 |
| LLM rate limits | Queue + retry with backoff |

---

## Related Documents

- [Configuration](./09-configuration.md)
- [Authentication & Sessions](./07-authentication-and-sessions.md)
- [Getting Started](./03-getting-started.md)
