# Sales AI Analyzer

سامانه تحلیل تماس‌های فروش با جریان زیر:

`Dynamics 365 → Redis/ARQ → FarsAva STT → LangGraph/OpenAI → PostgreSQL → Next.js`

## راه‌اندازی

1. فایل `.env.example` را به `.env` کپی و مقادیر واقعی را وارد کنید.
2. برای `POSTGRES_PASSWORD` و `APP_API_KEY` مقادیر تصادفی و طولانی انتخاب کنید.
3. دامنه میزبان فایل‌های صوتی webhook را در `AUDIO_URL_ALLOWED_HOSTS` وارد کنید.
4. سرویس‌ها را اجرا کنید:

```bash
docker compose up --build
```

داشبورد روی `http://localhost:3000` و API روی `http://localhost:8000` اجرا می‌شود.

## API

- `GET /api/health` — بررسی سلامت API
- `GET /api/calls/recent` — آخرین تحلیل‌ها
- `POST /api/sync-crm` — همگام‌سازی CRM
- `POST /api/webhook/dynamics` — افزودن تماس دارای URL صوتی به صف

دو endpoint نوشتنی به هدر زیر نیاز دارند:

```text
X-API-Key: <APP_API_KEY>
```

## دیتابیس

Migrationها پیش از اجرای backend توسط سرویس `migrate` اجرا می‌شوند:

```bash
docker compose run --rm migrate
```

## تست

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

## نکات امنیتی

- فایل `.env` را commit نکنید.
- اگر کلیدهای واقعی قبلاً منتشر شده‌اند، آن‌ها را rotate کنید.
- PostgreSQL و Redis فقط روی loopback میزبان publish شده‌اند.
- برای محیط production، TLS و یک reverse proxy احراز هویت‌شده اضافه کنید.
