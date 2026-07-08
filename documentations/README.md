# CURIO Documentation

Welcome to the official documentation for **CURIO** — *Content Using Research & Intelligent Output*.

CURIO is an AI-powered SaaS platform that discovers trending facts, researches them on the web, generates meme-style captions and images, and publishes the result as shareable social content for authenticated users.

---

## Documentation Index

| # | Document | Description |
|---|----------|-------------|
| 1 | [Overview](./01-overview.md) | Product vision, features, and platform summary |
| 2 | [Architecture](./02-architecture.md) | System design, tech stack, and data flow |
| 3 | [Getting Started](./03-getting-started.md) | Local setup, prerequisites, and first run |
| 4 | [Content Pipeline](./04-content-pipeline.md) | Seven-stage AI post generation workflow |
| 5 | [API Reference](./05-api-reference.md) | Complete REST API documentation |
| 6 | [Data Models](./06-data-models.md) | MongoDB collections and schema reference |
| 7 | [Authentication & Sessions](./07-authentication-and-sessions.md) | Sign-up, login, cookies, and security |
| 8 | [Frontend & UI](./08-frontend-and-ui.md) | Web pages, static assets, and UX flows |
| 9 | [Configuration](./09-configuration.md) | Environment variables and external services |
| 10 | [Project Structure](./10-project-structure.md) | Repository layout and module map |
| 11 | [Deployment](./11-deployment.md) | Production deployment guidance |
| 12 | [SaaS Features](./12-saas-features.md) | Multi-user, quotas, explore feed, and profiles |

---

## Quick Links

- **Run the server:** `python -m app.server` (from project root)
- **API base URL:** `http://localhost:5000/api`
- **Web UI:** `http://localhost:5000/auth`

---

## Legacy Note

The earlier `api_endpoints.md` file has been superseded by [05-api-reference.md](./05-api-reference.md), which includes search endpoints and corrected route details.
