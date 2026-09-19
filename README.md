# Auth API

A secured task-API foundation built with FastAPI and Supabase Auth, as part of the FlyRank Internship Backend track (W2 · A4). Users can sign up, log in, and log out — and specific routes only respond to requests carrying a valid, verified token.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Then open `.env` and fill in your own Supabase project's values:

```
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
PORT=8000
```

Find these under your Supabase Dashboard → Project Settings → API. Use the **anon** key only — never the `service_role` key, which bypasses all security and must never be used client-side or committed anywhere.

## Run

```bash
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Interactive docs (with a working "Authorize" bearer-token flow) at `http://localhost:8000/docs`.

## Endpoints

| Method | Path | Auth required | Description |
|---|---|---|---|
| GET | / | No | API info |
| POST | /auth/signup | No | Create a new user account |
| POST | /auth/login | No | Log in, get an access token |
| POST | /auth/logout | Yes | End the current session |
| GET | /public/info | No | Open, public data |
| GET | /protected/profile | Yes | Get the logged-in user's profile |
| GET | /protected/dashboard | Yes | Second protected route, same guard |

## Example flow

```bash
curl -i -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

```
HTTP/1.1 201 Created
content-type: application/json

{"user": {"id": "...", "email": "test@example.com", ...}}
```

```bash
curl -i -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

```
HTTP/1.1 200 OK
content-type: application/json

{"access_token": "eyJ...", "refresh_token": "..."}
```

```bash
curl -i http://localhost:8000/protected/profile \
  -H "Authorization: Bearer <access_token>"
```

```
HTTP/1.1 200 OK
content-type: application/json

{"id": "...", "email": "test@example.com", "created_at": "..."}
```

## How verification works

Your server never touches or stores a password. Sign-up and login credentials are forwarded straight to Supabase, which handles hashing, storage, and issuing a signed JWT. Protected routes extract the token from the `Authorization: Bearer <token>` header and ask Supabase directly — via `supabase.auth.get_user(token)` — whether it's genuine. A missing, malformed, tampered, or expired token is rejected with `401` before the route's own logic ever runs; this check lives in one reusable FastAPI dependency (`get_current_user`), applied to every protected route rather than duplicated per-route.

## Swagger UI

`/docs` shows a padlock icon next to every protected route. Clicking "Authorize" and pasting a token lets you call protected endpoints directly from the browser, no curl needed.

![Swagger UI with Authorize dialog](swagger-auth-screenshot.png)

## Security notes

- `.env` holds real secrets and is git-ignored; `.env.example` documents the required keys with placeholders only.
- Only the Supabase `anon` key is used anywhere in this project — it's designed to be safe in client-facing code. The `service_role` key was never generated or used.