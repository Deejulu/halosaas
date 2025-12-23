# Restaurant SaaS

Local development quick notes:

- Copy `.env.example` to `.env` and fill values.
- Run development server:

```bash
python manage.py runserver
```

Paystack notes:

- Use test keys for local testing (`PAYSTACK_PUBLIC_KEY`, `PAYSTACK_SECRET_KEY`).
- Set `PAYSTACK_WEBHOOK_SECRET` in production and register your webhook URL in Paystack dashboard.
- The app verifies Paystack webhook signatures using HMAC-SHA512.
