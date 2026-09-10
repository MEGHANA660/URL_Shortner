# URL Shortener & Analytics API

A backend service that converts long URLs into short, unique codes and tracks click analytics — built with FastAPI, PostgreSQL, and Redis, fully containerized with Docker and deployed on Railway.

**Live demo:** https://urlshortner-production-440d.up.railway.app/docs
**Repo:** https://github.com/MEGHANA660/URL_Shortner

---

## Features

- **Custom Base62 short-code generation** — encodes auto-incrementing database IDs into short, URL-safe codes (no collision handling needed, since it's a bijection)
- **Redirect tracking** — every visit to a short link is logged with a timestamp for analytics
- **Cache-aside caching with Redis** — frequently accessed short codes are served from cache instead of hitting Postgres on every redirect
- **Rate limiting** — IP-based request throttling on URL creation to prevent abuse (returns `429 Too Many Requests` when exceeded)
- **Click analytics endpoint** — returns total click count for any short code
- **Fully containerized** — API, PostgreSQL, and Redis all run as isolated services via Docker Compose

---

## Tech Stack

| Layer            | Technology            |
|-------------------|------------------------|
| API Framework     | FastAPI (Python)       |
| Database          | PostgreSQL             |
| ORM               | SQLAlchemy             |
| Caching / Rate Limiting | Redis            |
| Containerization  | Docker, Docker Compose |
| Deployment        | Railway                |

---

## API Endpoints

| Method | Endpoint          | Description                                  |
|--------|-------------------|-----------------------------------------------|
| POST   | `/shorten`        | Create a short code for a given long URL      |
| GET    | `/{code}`         | Redirect to the original URL; logs a click    |
| GET    | `/stats/{code}`   | Get total click count for a short code        |

### Example — Create a short URL

**Request**
```http
POST /shorten
Content-Type: application/json

{
  "long_url": "https://www.wikipedia.org"
}
```

**Response**
```json
{
  "short_code": "3",
  "long_url": "https://www.wikipedia.org"
}
```

### Example — Get stats

**Request**
```http
GET /stats/3
```

**Response**
```json
{
  "short_code": "3",
  "long_url": "https://www.wikipedia.org",
  "total_clicks": 4
}
```

---

## Design Decisions

**Why Base62 encoding on auto-increment IDs instead of random generation or hashing?**
Since each shortened link is always meant to get a new, unique code (no deduplication of repeated long URLs), encoding the database's auto-incrementing primary key guarantees uniqueness with zero collision risk — no need for a "generate → check → retry" loop. The trade-off is that codes are sequential and technically guessable; in a production system, this could be mitigated by offsetting or obfuscating the ID before encoding.

**Why cache-aside instead of write-through caching?**
Redirects are read-heavy and the underlying URL data rarely changes after creation, so caching on first read (cache-aside) avoids unnecessary cache writes for links that are created but never clicked.

**Why log clicks synchronously inside the redirect endpoint?**
For this scale, a synchronous insert keeps the implementation simple and consistent. At higher traffic, this would be a good candidate to move to an async task queue (e.g., Celery) to avoid adding latency to the redirect path.

---

## Running Locally

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (only needed if running outside Docker)

### Steps

1. Clone the repository
   ```bash
   git clone https://github.com/MEGHANA660/URL_Shortner.git
   cd URL_Shortner
   ```

2. Create a `.env` file in the project root:
   ```
   DATABASE_URL=postgresql://myuser:mypassword@postgres:5432/urlshortener
   REDIS_URL=redis://redis:6379
   ```

3. Build and run all services:
   ```bash
   docker compose up --build
   ```

4. The API will be available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

---

## Project Structure

```
url-shortener/
├── app/
│   ├── main.py           # FastAPI app and endpoints
│   ├── database.py       # SQLAlchemy engine/session setup
│   ├── models.py         # URL and Click ORM models
│   ├── schemas.py        # Pydantic request/response schemas
│   └── core/
│       └── shortcode.py  # Base62 encode/decode logic
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Author

Built by Meghana K as a backend portfolio project, focused on demonstrating REST API design, caching strategy, rate limiting, and Docker-based deployment.
