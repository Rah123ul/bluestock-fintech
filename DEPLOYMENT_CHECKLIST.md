# Deployment Checklist (Django 4.2 → Railway)

- [ ] All essential environment variables are set in the Railway dashboard (`DATABASE_URL`, `SECRET_KEY`, etc.)
- [ ] `DEBUG` is set to `False` in production `settings.py` (or via env var)
- [ ] `ALLOWED_HOSTS` includes your Railway project domain (`*.up.railway.app` or custom domain)
- [ ] `python manage.py collectstatic --noinput` runs successfully before or during deployment
- [ ] `python manage.py migrate` is executed successfully against the Railway PostgreSQL database
- [ ] A Django admin superuser has been successfully created
- [ ] All updated API endpoints (`/charts/`, `/screener/`, `/health-scores/`) return 200 OK with correct JSON data
- [ ] All website frontend pages are rendering completely (no broken static files or missing images)
