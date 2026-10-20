# Application Inventory System

A production-style **Django + PostgreSQL** web application for tracking an
organization's software application portfolio: ownership, vendors,
deployments, licenses, costs, and lifecycle status — with a dashboard, a
searchable/filterable catalog, a full REST API, and the Django admin.

![Stack](https://img.shields.io/badge/Django-5.2%20LTS-092E20?logo=django)
![DB](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql)
![API](https://img.shields.io/badge/API-Django%20REST%20Framework-red)

---

## ✨ Features

- **Dashboard** — KPI cards + Chart.js visualizations (status, criticality,
  hosting type, category spend, department spend, top costs, recent apps).
- **Dark mode** — toggle in the navbar, remembers your preference, follows
  system preference on first visit.
- **Application catalog** — searchable, filterable (category, vendor,
  department, status, criticality, type, hosting, cost range), paginated
  card grid.
- **Rich data model** — Applications, Vendors, Departments, Categories, Tags,
  Environments, Deployments (servers), Licenses, and an Audit Log.
- **Detail pages** — full application profile, deployments across
  environments, license seat usage, and change history.
- **CRUD** — create/edit/delete applications, add deployments & licenses
  (login required; Bootstrap 5 forms via django-crispy-forms).
- **Reports** — cost by category, deployments by environment, licenses
  expiring soon, apps nearing end-of-life.
- **REST API** — full CRUD for every resource via Django REST Framework,
  with filtering (`django-filter`), search, ordering, pagination, and a
  `/api/applications/stats/` aggregate endpoint. Browsable API included.
- **Django Admin** — customized list views, inline deployments/licenses,
  colored status/criticality badges, autocomplete fields.
- **Dummy data seeder** — one command populates ~30 realistic applications
  across 12 categories, 20 vendors, 8 departments, 5 environments, ~75
  deployments, and ~25 licenses.
- **PostgreSQL-first** — configured for Postgres via environment variables,
  with an optional SQLite fallback for quick local demos.
- **Docker Compose** — one command spins up Postgres + the web app.

---

## 🗂 Project Structure

```
app_inventory/
├── inventory_project/       # Django project (settings, urls, wsgi/asgi)
├── applications/             # Main app
│   ├── models.py             # Application, Vendor, Department, Category,
│   │                          # Tag, Environment, Deployment, License, AuditLogEntry
│   ├── views.py               # Dashboard, list/detail/CRUD, reports
│   ├── admin.py                # Rich Django admin config
│   ├── forms.py                 # Crispy ModelForms
│   ├── filters.py                # django-filter FilterSets
│   ├── serializers.py             # DRF serializers
│   ├── api_views.py                # DRF ViewSets
│   ├── api_urls.py                  # DRF router
│   ├── urls.py                       # Web URLs
│   ├── context_processors.py          # Navbar stats
│   └── management/commands/seed_data.py  # Dummy data generator
├── templates/                # Bootstrap 5 templates
├── static/css/styles.css      # Custom styling
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── manage.py
```

---

## 🚀 Quick Start (local, with PostgreSQL)

### 1. Prerequisites
- Python 3.11+
- PostgreSQL 13+ running locally (or use Docker — see below)

### 2. Clone / unzip and set up a virtual environment

```bash
cd app_inventory
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create the PostgreSQL database

```bash
psql -U postgres -c "CREATE DATABASE app_inventory_db;"
```

### 4. Configure environment variables

```bash
cp .env.example .env
# edit .env and set DB_USER / DB_PASSWORD / DB_HOST to match your Postgres instance
```

For hosted deployments, you can set `DATABASE_URL` instead of the individual
database settings. Set `CSRF_TRUSTED_ORIGINS` to a comma-separated list of
trusted HTTPS origins, for example `https://inventory.example.com`.

### 5. Run migrations, seed dummy data, and start the server

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver
```

Visit:
- **App:** http://127.0.0.1:8000/
- **Admin:** http://127.0.0.1:8000/admin/
- **API root:** http://127.0.0.1:8000/api/

Sign in using the superuser account created above. User accounts are managed by an administrator; there is no public sign-up.

---

## 🐳 Quick Start (Docker Compose)

This spins up PostgreSQL **and** the Django app, runs migrations, seeds
dummy data, and serves via Gunicorn:

```bash
docker compose up --build
```

In a second terminal, create an account with
`docker compose exec web python manage.py createsuperuser`, then visit
http://localhost:8000/ and sign in. User accounts are managed by an administrator; there is no public sign-up.

---

## 🧪 Quick Start (no PostgreSQL — SQLite demo mode)

If you just want to preview the UI without installing Postgres:

```bash
export USE_SQLITE=True        # Windows (PowerShell): $env:USE_SQLITE="True"
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver
```

> Set `USE_SQLITE=False` (or remove it) to go back to PostgreSQL — this is
> meant for quick local previews only, not production use.

---

## 🔁 Re-seeding

To wipe and regenerate dummy data:

```bash
python manage.py seed_data --flush
```

---

## 🔌 REST API

All endpoints are under `/api/`, browsable in-browser, and support
`?search=`, `?ordering=`, and field-based filters, e.g.:

| Endpoint | Description |
|---|---|
| `GET /api/applications/` | List applications (paginated, filterable) |
| `GET /api/applications/{slug}/` | Full application detail |
| `POST /api/applications/` | Create an application (auth required) |
| `GET /api/applications/stats/` | Aggregate portfolio stats |
| `GET /api/vendors/`, `/api/categories/`, `/api/departments/`, `/api/tags/` | Reference data |
| `GET /api/deployments/`, `/api/licenses/`, `/api/environments/` | Related resources |

Examples:
```bash
curl "http://127.0.0.1:8000/api/applications/?status=ACTIVE&criticality=CRITICAL"
curl "http://127.0.0.1:8000/api/applications/?search=salesforce"
curl "http://127.0.0.1:8000/api/applications/stats/"
```

---

## 🛠 Tech Stack

- **Backend:** Django 5.2 (LTS), Django REST Framework, django-filter
- **Database:** PostgreSQL 16 (psycopg2-binary driver)
- **Frontend:** Django templates, **Tailwind CSS** (via CDN, no Node build step required), Bootstrap Icons, Chart.js, django-crispy-forms (crispy-tailwind)
- **Config:** python-decouple (12-factor `.env` config)
- **Data generation:** Faker-style handcrafted realistic dummy dataset
- **Containerization:** Docker + Docker Compose

---

## 📌 Notes for Production Use

- Set `DEBUG=False` and a strong random `SECRET_KEY` in `.env`.
- Set `ALLOWED_HOSTS` to your real domain(s).
- Set `CSRF_TRUSTED_ORIGINS` to your HTTPS site origin(s). WhiteNoise serves
  collected static files using compressed, manifest-based storage.
- Run `python manage.py collectstatic` during deployment.
- Put PostgreSQL behind proper backups and connection pooling (e.g.
  PgBouncer) for larger deployments.
- Consider adding `django-axes` or similar for login rate-limiting before
  exposing the admin/login publicly.
- This project loads Tailwind CSS via the CDN `<script src="https://cdn.tailwindcss.com">`
  for zero-build-step simplicity. That's great for development/demos, but
  the CDN build is unminified and includes the whole utility set. For a
  real production deployment, consider installing `django-tailwind` or the
  standalone Tailwind CLI and compiling a purged, minified CSS file instead.
