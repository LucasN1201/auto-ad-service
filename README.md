# Auto-ad Service

System for collecting car ads from carsensor.net with an API, admin panel, and Telegram bot.

## Launch (one command)

```bash
docker-compose up --build
```

- **Admin panel:** http://localhost:3000  
- **API:** http://localhost:8000  
- **API docs:** http://localhost:8000/docs  

### Default admin login

- **Username:** `admin`  
- **Password:** `admin123`  

Use these on the login page at http://localhost:3000/login. Change in production via `ADMIN_USERNAME` / `ADMIN_PASSWORD` (and re-seed or change password in DB).

### Environment

Copy `.env.example` to `.env` and set at least:

- `TELEGRAM_BOT_TOKEN` — from [@BotFather](https://t.me/BotFather)
- `OPENAI_API_KEY` — for the Telegram bot’s LLM

Then run:

```bash
docker-compose up --build
```

---

## Architecture

### 1. Backend & Scraper (Python/FastAPI)

- **API:** FastAPI with JWT auth.
  - `POST /api/login` — body `{ "username", "password" }`, returns `{ "access_token" }`.
  - `GET /api/cars` — returns list of cars; requires `Authorization: Bearer <token>`.
- **Database:** PostgreSQL. Migrations with Alembic. Default admin is created in the first migration.
- **Worker:** Separate process that periodically fetches new listings from carsensor.net, parses make/model/year/price/color/link, and **upserts** by `link` (update existing, insert new). Retries on network errors (3 attempts with backoff).

### 2. Frontend (Next.js)

- **SPA:** Next.js 14 (App Router), Tailwind CSS.
- **Routes:**
  - `/login` — login form; stores JWT in `localStorage` and redirects to `/`.
  - `/` — protected; shows car table from `GET /api/cars`. Redirects to `/login` if not authenticated.
- **UI:** Responsive, modern layout; table works on mobile with horizontal scroll where needed.

### 3. Telegram bot

- Accepts free-form messages (e.g. “Find a red BMW up to 2 million”).
- Uses **OpenAI** with **function calling**: the LLM extracts `make`, `model`, `color`, `price_max`, `year_min`/`year_max`, etc.
- Runs a filtered query on the same PostgreSQL `cars` table and replies with a readable list (make, model, year, price, color, link).
- If `OPENAI_API_KEY` is missing, the bot replies asking to set it or to request a key.

### 4. Delivery

- **Run:** `docker-compose up --build`.
- **Repo:** Public; `.env.example` documents all variables.
- **README:** This file (launch, admin credentials, architecture).

---

## Project layout

```
backend/          # FastAPI app, Alembic, scraper, worker
frontend/         # Next.js admin SPA
telegram_bot/     # Telegram bot + LLM + DB query
docker-compose.yml
.env.example
README.md
```

## Local development (without Docker)

1. **DB:** Start PostgreSQL, create DB `autoad`.
2. **Backend:** `cd backend && pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --reload`
3. **Worker:** `cd backend && python -m app.worker` (optional, in another terminal).
4. **Frontend:** `cd frontend && npm i && npm run dev` — set `NEXT_PUBLIC_API_URL=http://localhost:8000`.
5. **Bot:** `cd telegram_bot && pip install -r requirements.txt` — set `DATABASE_URL`, `TELEGRAM_BOT_TOKEN`, `OPENAI_API_KEY` in `.env`, then `python bot.py`.
