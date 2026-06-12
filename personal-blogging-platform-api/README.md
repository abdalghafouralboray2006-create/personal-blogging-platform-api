# Personal Blogging Platform API

A secure, production-quality REST API for a personal blogging platform, built with **Node.js**, **Express**, **PostgreSQL**, and **Prisma**. Designed to be simple, clean, and deployable on **Vercel** with **Neon PostgreSQL**.

## Features

- User registration & login with JWT authentication
- Passwords hashed with bcrypt (never stored in plaintext)
- Public post listing, protected create/update/delete
- Ownership enforcement (403 if you try to edit/delete someone else's post)
- Centralized error handling with consistent JSON responses
- Request validation with express-validator
- Rate limiting on the login endpoint (5 attempts / 15 minutes / IP)
- UUID primary keys for all records
- SQL injection protection via Prisma's parameterized queries

## Tech Stack

- Node.js + Express.js (plain JavaScript, no TypeScript)
- PostgreSQL (Neon-compatible)
- Prisma ORM
- bcrypt
- jsonwebtoken
- express-validator
- express-rate-limit
- dotenv

## Folder Structure

```
src/
├── controllers/    # Request handlers (auth, posts)
├── routes/         # Express route definitions
├── middleware/      # Auth, validation, error handling
├── validators/      # express-validator rule sets
├── database/        # Prisma client singleton
├── services/        # Business logic
├── utils/           # AppError, response helpers, async wrapper
├── config/          # Env loading, rate limiter config
├── app.js           # Express app assembly
└── server.js        # Local dev entry point
api/
└── index.js          # Vercel serverless entry point
prisma/
└── schema.prisma     # Database schema
```

## 1. Installation

```bash
git clone <your-repo-url>
cd blog-api
npm install
```

## 2. Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

| Variable         | Description                                       | Example                                              |
|------------------|----------------------------------------------------|-------------------------------------------------------|
| `DATABASE_URL`   | PostgreSQL connection string (Neon recommended)   | `postgresql://user:pass@host/db?sslmode=require`     |
| `JWT_SECRET`     | Secret used to sign JWT tokens                    | A long random string (`openssl rand -base64 48`)    |
| `JWT_EXPIRES_IN` | Access token lifetime                             | `1h`                                                  |
| `PORT`           | Local server port (ignored on Vercel)             | `3000`                                                |
| `NODE_ENV`       | `development` or `production`                     | `development`                                        |

## 3. Database Setup

### Option A — Prisma Migrations (recommended)

```bash
npx prisma migrate dev --name init
npx prisma generate
```

This creates the `users` and `posts` tables automatically based on `prisma/schema.prisma`.

### Option B — Manual SQL

Run the SQL in [`database_schema.sql`](./database_schema.sql) directly against your PostgreSQL database (e.g. via the Neon SQL editor or `psql`). Then run:

```bash
npx prisma generate
```

so the Prisma client matches the existing tables.

## 4. Running Locally

```bash
npm run dev
```

The API will be available at `http://localhost:3000`.

To run in production mode locally:

```bash
npm start
```

## 5. Deployment (Vercel + Neon)

1. **Create a Neon database**: sign up at [neon.tech](https://neon.tech), create a project, and copy the connection string (use the pooled connection string with `sslmode=require`).
2. **Push your code to GitHub.**
3. **Import the repo into Vercel** (vercel.com → New Project → select your repo).
4. **Set environment variables** in Vercel project settings:
   - `DATABASE_URL` — your Neon connection string
   - `JWT_SECRET` — a long random secret
   - `JWT_EXPIRES_IN` — e.g. `1h`
   - `NODE_ENV` — `production`
5. **Run migrations against Neon** before/after first deploy (from your local machine, with `DATABASE_URL` pointing at Neon):
   ```bash
   npx prisma migrate deploy
   ```
6. Vercel will run `npm run build` (which runs `prisma generate`), and route all requests through `api/index.js` via `vercel.json`.
7. Your API will be live at `https://<your-project>.vercel.app`.

## API Endpoints

Base URL (local): `http://localhost:3000`

| Method | Endpoint          | Auth required | Description                          |
|--------|-------------------|---------------|--------------------------------------|
| POST   | `/auth/register`  | No            | Register a new user                   |
| POST   | `/auth/login`     | No            | Log in and receive a JWT token        |
| GET    | `/posts`          | No            | List all posts                        |
| POST   | `/posts`          | Yes           | Create a new post                     |
| PUT    | `/posts/:id`      | Yes (owner)   | Update a post you own                 |
| DELETE | `/posts/:id`      | Yes (owner)   | Delete a post you own                 |

### Authentication

Protected routes require:

```
Authorization: Bearer <token>
```

---

### POST /auth/register

**Request body:**

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "password": "Secur3!pass"
}
```

**Validation rules:**
- `name`: required, non-empty
- `email`: required, valid email format, must be unique
- `password`: minimum 8 characters, at least one number, at least one special character

**Success response — 201 Created:**

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "b3f1c6f0-2b5b-4d8f-9d8e-7e2c1a2f9a11",
      "name": "Jane Doe",
      "email": "jane@example.com",
      "createdAt": "2026-06-12T10:00:00.000Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error response — 400 Bad Request (duplicate email):**

```json
{
  "success": false,
  "message": "Email is already registered"
}
```

**Error response — 400 Bad Request (validation):**

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    { "field": "password", "message": "Password must contain at least one number" }
  ]
}
```

---

### POST /auth/login

Rate limited to **5 attempts per 15 minutes per IP**.

**Request body:**

```json
{
  "email": "jane@example.com",
  "password": "Secur3!pass"
}
```

**Success response — 200 OK:**

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": "b3f1c6f0-2b5b-4d8f-9d8e-7e2c1a2f9a11",
      "name": "Jane Doe",
      "email": "jane@example.com",
      "createdAt": "2026-06-12T10:00:00.000Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Error response — 401 Unauthorized:**

```json
{
  "success": false,
  "message": "Invalid email or password"
}
```

**Error response — 429 Too Many Requests:**

```json
{
  "success": false,
  "message": "Too many login attempts. Please try again after 15 minutes."
}
```

---

### GET /posts

Public endpoint. Returns all posts, most recent first.

**Success response — 200 OK:**

```json
{
  "success": true,
  "data": [
    {
      "id": "a1b2c3d4-e5f6-4a1b-8c9d-0e1f2a3b4c5d",
      "title": "My First Post",
      "content": "Hello, world!",
      "authorId": "b3f1c6f0-2b5b-4d8f-9d8e-7e2c1a2f9a11",
      "createdAt": "2026-06-12T10:05:00.000Z",
      "updatedAt": "2026-06-12T10:05:00.000Z",
      "author": {
        "id": "b3f1c6f0-2b5b-4d8f-9d8e-7e2c1a2f9a11",
        "name": "Jane Doe"
      }
    }
  ]
}
```

---

### POST /posts

Protected. Requires `Authorization: Bearer <token>`.

**Request body:**

```json
{
  "title": "My First Post",
  "content": "Hello, world!"
}
```

**Validation rules:**
- `title`: required, non-empty
- `content`: required, non-empty

**Success response — 201 Created:**

```json
{
  "success": true,
  "message": "Post created successfully",
  "data": {
    "id": "a1b2c3d4-e5f6-4a1b-8c9d-0e1f2a3b4c5d",
    "title": "My First Post",
    "content": "Hello, world!",
    "authorId": "b3f1c6f0-2b5b-4d8f-9d8e-7e2c1a2f9a11",
    "createdAt": "2026-06-12T10:05:00.000Z",
    "updatedAt": "2026-06-12T10:05:00.000Z",
    "author": {
      "id": "b3f1c6f0-2b5b-4d8f-9d8e-7e2c1a2f9a11",
      "name": "Jane Doe"
    }
  }
}
```

**Error response — 401 Unauthorized:**

```json
{
  "success": false,
  "message": "Authentication token is missing"
}
```

---

### PUT /posts/:id

Protected. Only the post's owner can update it.

**Request body (at least one field required):**

```json
{
  "title": "Updated Title",
  "content": "Updated content."
}
```

**Success response — 200 OK:**

```json
{
  "success": true,
  "message": "Post updated successfully",
  "data": {
    "id": "a1b2c3d4-e5f6-4a1b-8c9d-0e1f2a3b4c5d",
    "title": "Updated Title",
    "content": "Updated content.",
    "authorId": "b3f1c6f0-2b5b-4d8f-9d8e-7e2c1a2f9a11",
    "createdAt": "2026-06-12T10:05:00.000Z",
    "updatedAt": "2026-06-12T10:10:00.000Z",
    "author": {
      "id": "b3f1c6f0-2b5b-4d8f-9d8e-7e2c1a2f9a11",
      "name": "Jane Doe"
    }
  }
}
```

**Error response — 403 Forbidden (not the owner):**

```json
{
  "success": false,
  "message": "You do not have permission to modify this post"
}
```

**Error response — 404 Not Found:**

```json
{
  "success": false,
  "message": "Post not found"
}
```

---

### DELETE /posts/:id

Protected. Only the post's owner can delete it.

**Success response — 200 OK:**

```json
{
  "success": true,
  "message": "Post deleted successfully",
  "data": null
}
```

**Error response — 403 Forbidden (not the owner):**

```json
{
  "success": false,
  "message": "You do not have permission to delete this post"
}
```

---

## Error Response Format

All errors follow this shape:

```json
{
  "success": false,
  "message": "Description of the error",
  "errors": [
    { "field": "email", "message": "Email must be a valid email address" }
  ]
}
```

`errors` is only present for validation failures (400).

## HTTP Status Codes Used

| Code | Meaning               | Example                                      |
|------|-----------------------|-----------------------------------------------|
| 200  | OK                     | Successful GET/PUT/DELETE                     |
| 201  | Created                | Successful registration or post creation      |
| 400  | Bad Request            | Validation errors, duplicate email            |
| 401  | Unauthorized           | Missing/invalid token, bad login credentials  |
| 403  | Forbidden              | Attempting to modify/delete another user's post |
| 404  | Not Found              | Post or route does not exist                  |
| 429  | Too Many Requests      | Exceeded login rate limit                     |
| 500  | Internal Server Error  | Unexpected server/database error              |

## Security Notes

- Passwords are hashed with bcrypt (10 salt rounds) and never returned in API responses.
- JWT secret is loaded from environment variables, never hardcoded.
- All database queries go through Prisma's parameterized query builder, preventing SQL injection.
- All primary keys are UUIDs generated by the database.
- Login endpoint is rate-limited to mitigate brute-force attacks.

## License

MIT
