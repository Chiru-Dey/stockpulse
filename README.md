# StockPulse — Retail Inventory Management Dashboard

StockPulse is a full-stack web application for managing retail inventory. Instead of editing stock quantities directly, every change in stock is recorded as a stock movement (IN or OUT), and the current stock level is calculated from those movements. This gives a complete, auditable history of all inventory activity.

Built with Flask + SQLAlchemy on the backend and Vue 3 + Tailwind CSS on the frontend, with JWT-based authentication and role-based access control (admin vs staff).

## Project Overview

- **Domain:** retail / e-commerce operations / warehouse management
- **Backend:** RESTful API (Flask), SQLite database, JWT auth (access + refresh tokens), Argon2 password hashing
- **Frontend:** single-page app (Vue 3 + Vite), Pinia auth store, Vue Router with protected routes, Axios API client
- **Key business rules:**
  - Stock quantity is never edited directly; it is derived from StockMovement records
  - OUT movements cannot exceed current stock
  - Categories that still contain products cannot be deleted
  - Admins manage products and categories; staff can view everything and record stock movements

## Features

- User registration and login with JWT access / refresh tokens
- Role-based UI and API protection (admin vs staff)
- Product CRUD with category assignment and low-stock threshold
- Category CRUD with delete protection
- Stock IN / OUT movement recording with server-side validation
- Live stock calculation with status badges (OK / LOW / OUT)
- Dashboard with total products, total stock units, low-stock count, out-of-stock count and recent activity
- Filtering: products by name/SKU, category and stock status; movements by product, type and date range
- Pagination on product and movement lists
- Seed script that generates realistic demo data

## Tech Stack

| Layer    | Technology |
|----------|------------|
| Backend  | Python 3.12, Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-CORS, Argon2 (argon2-cffi) |
| Frontend | Vue 3 (Composition API), Vite, Vue Router 4, Pinia, Axios, Tailwind CSS 3, Heroicons |
| Database | SQLite (development) |
| Tooling  | uv (Python package manager), npm (Node) |

## Repository Structure

stockpulse/
├── app/
│   ├── __init__.py          # App factory, blueprint registration
│   ├── extensions.py        # db, jwt, cors instances
│   ├── models.py            # User, Category, Product, StockMovement
│   ├── utils.py             # admin_required decorator
│   └── api/
│       ├── auth.py          # register / login / refresh / me
│       ├── categories.py    # category CRUD
│       ├── products.py      # product CRUD + filters + pagination
│       ├── movements.py     # movement list + create
│       └── dashboard.py     # summary statistics
├── frontend/
│   ├── src/
│   │   ├── api/             # axios client + per-resource services
│   │   ├── components/      # AppLayout, StatCard, MovementTable, ProductFormModal
│   │   ├── router/          # routes + auth guards
│   │   ├── stores/          # Pinia auth store
│   │   ├── views/           # Login, Dashboard, Products, Categories, Movements
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css        # Tailwind entry point
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
├── config.py                # configuration from environment variables
├── wsgi.py                  # Flask entry point
├── setup_db.py              # creates database tables
├── seed.py                  # demo data generator
├── .env                     # local secrets (not committed)
└── pyproject.toml           # uv project file

## Installation

### Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/) installed
- Node.js 18+ with npm
- Git

### 1. Clone the repository

git clone <your-repo-url>
cd stockpulse

### 2. Backend setup

Windows PowerShell:

uv venv
.venv\Scripts\activate
uv sync

macOS / Linux:

uv venv
source .venv/bin/activate
uv sync

Create a `.env` file in the project root with the following content (replace secrets for any real deployment):

SECRET_KEY=local-dev-secret-key
JWT_SECRET_KEY=stockpulse-super-secret-jwt-key-for-local-dev-2026
ACCESS_TOKEN_HOURS=12
REFRESH_TOKEN_DAYS=30
CORS_ORIGINS=http://localhost:5173

Create the database tables and load demo data:

uv run python setup_db.py
uv run python seed.py

Start the API server (serves on http://127.0.0.1:5000):

uv run python wsgi.py

### 3. Frontend setup

In a second terminal:

cd frontend
npm install
npm run dev

Open http://localhost:5173 in your browser.

### Demo accounts

| Role  | Email                | Password    |
|-------|----------------------|-------------|
| Admin | admin@stockpulse.com | password123 |
| Staff | staff@stockpulse.com | password123 |

Admins can create, edit and delete products and categories. Staff can view everything and record stock movements.

### Environment variables

| Variable           | Purpose                                  | Default                          |
|--------------------|------------------------------------------|----------------------------------|
| SECRET_KEY         | Flask secret key                         | local-dev-secret-key             |
| JWT_SECRET_KEY     | JWT signing key (use 32+ characters)     | falls back to SECRET_KEY         |
| ACCESS_TOKEN_HOURS | Access token lifetime in hours           | 12                               |
| REFRESH_TOKEN_DAYS | Refresh token lifetime in days           | 30                               |
| CORS_ORIGINS       | Comma-separated list of allowed origins  | http://localhost:5173            |
| DATABASE_URL       | SQLAlchemy database URL                  | sqlite:///instance/stockpulse.db |

## API Documentation

Base URL: `http://127.0.0.1:5000/api`

All endpoints except `/health`, `/auth/register` and `/auth/login` require the header `Authorization: Bearer <access_token>`. Endpoints marked **(admin)** additionally require the authenticated user to be an admin.

All errors are returned as JSON: `{"error": "message"}` with an appropriate HTTP status code.

### Health

| Method | Path    | Auth | Description           |
|--------|---------|------|-----------------------|
| GET    | /health | No   | Service health check  |

### Authentication

| Method | Path           | Auth            | Description                          |
|--------|----------------|-----------------|--------------------------------------|
| POST   | /auth/register | No              | Create account, returns user + tokens |
| POST   | /auth/login    | No              | Log in, returns user + tokens         |
| POST   | /auth/refresh  | Refresh token   | Issue a new access token              |
| GET    | /auth/me       | Yes             | Current user profile                  |

Register / login request body:

{ "email": "admin@stockpulse.com", "password": "password123" }

Register / login response (201 / 200):

{
  "user": { "id": 1, "email": "admin@stockpulse.com", "is_admin": true, "created_at": "..." },
  "access_token": "<jwt>",
  "refresh_token": "<jwt>"
}

### Categories

| Method | Path             | Auth  | Description                              |
|--------|------------------|-------|------------------------------------------|
| GET    | /categories      | Yes   | List all (optional `?search=`)           |
| GET    | /categories/<id> | Yes   | Get one category                         |
| POST   | /categories      | admin | Create category                          |
| PATCH  | /categories/<id> | admin | Partial update                           |
| DELETE | /categories/<id> | admin | Delete (400 if it still has products)    |

Create / update body:

{ "name": "Electronics", "description": "Gadgets and devices" }

### Products

| Method | Path           | Auth  | Description                              |
|--------|----------------|-------|------------------------------------------|
| GET    | /products      | Yes   | List with filters and pagination         |
| GET    | /products/<id> | Yes   | Get one product                          |
| POST   | /products      | admin | Create product                           |
| PATCH  | /products/<id> | admin | Partial update                           |
| DELETE | /products/<id> | admin | Delete (also deletes its movements)      |

Query parameters for GET /products: `search` (name or SKU), `category_id`, `stock_status` (`ok` | `low` | `out`), `page`, `per_page`.

Create / update body:

{
  "name": "Gaming Laptop",
  "sku": "EL-LAP-01",
  "description": "16 inch gaming laptop",
  "category_id": 1,
  "low_stock_threshold": 5
}

List response:

{
  "products": [
    {
      "id": 1,
      "name": "Gaming Laptop",
      "sku": "EL-LAP-01",
      "description": "16 inch gaming laptop",
      "category_id": 1,
      "low_stock_threshold": 5,
      "current_stock": 5,
      "stock_status": "low",
      "created_at": "...",
      "updated_at": "..."
    }
  ],
  "total": 6,
  "page": 1,
  "per_page": 10,
  "pages": 1
}

### Stock Movements

| Method | Path                 | Auth | Description                        |
|--------|----------------------|------|------------------------------------|
| GET    | /stock-movements     | Yes  | List with filters and pagination   |
| GET    | /stock-movements/<id>| Yes  | Get one movement                   |
| POST   | /stock-movements     | Yes  | Record an IN or OUT movement       |

Query parameters for GET: `product_id`, `movement_type` (`IN` | `OUT`), `date_from` (YYYY-MM-DD), `date_to` (YYYY-MM-DD, inclusive of that day), `page`, `per_page`.

Create body:

{ "product_id": 1, "movement_type": "OUT", "quantity": 5, "note": "Sold to customer" }

Validation rules:
- `quantity` must be a positive integer
- An `OUT` quantity greater than current stock returns 400: `{"error": "Insufficient stock", "current_stock": 15}`

### Dashboard

| Method | Path               | Auth | Description                                  |
|--------|--------------------|------|----------------------------------------------|
| GET    | /dashboard/summary | Yes  | Aggregate stats + 5 most recent movements    |

Response:

{
  "total_categories": 3,
  "total_products": 6,
  "total_stock_units": 105,
  "low_stock_count": 3,
  "out_of_stock_count": 1,
  "recent_movements": [ ]
}

## Future Improvements

- Daily low-stock report email as a Celery + Redis background job (optional item from the project brief)
- Supplier management and purchase orders
- CSV export of movement history
- PostgreSQL support for production deployments