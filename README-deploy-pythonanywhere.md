# Deploying Halo Sass to PythonAnywhere

This README explains step-by-step how to deploy this Django project to PythonAnywhere (PA).

Pre-reqs
- A PythonAnywhere account (paid for custom domain/HTTPS if using your domain).
- Your project repository accessible (GitHub/GitLab) or a ZIP of the project.
- A requirements.txt file at project root.

1) Upload/clone your project
- On PA Dashboard > Consoles open a Bash console.

Recommended: clone your repo
```bash
cd ~
git clone <YOUR_REPO_URL> site
cd site
```

Or upload a ZIP in Files and extract to `~/site`.

2) Create a virtualenv
```bash
python3.11 -m venv ~/.virtualenvs/restaurant-env
source ~/.virtualenvs/restaurant-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
(adjust python version to one available on PA)

3) Environment variables
- In the Web tab, open "Environment variables" and add the vars from `.env.example` (or upload a `.env` and load it in WSGI as shown below).

Required at minimum:
- `SECRET_KEY` (strong secret)
- `DEBUG=False`
- `ALLOWED_HOSTS=yourdomain.com`
- Database vars or `DATABASE_URL` (if using external DB)

4) Edit the WSGI file
- In the Web tab click the WSGI config file link (e.g. `/var/www/yourusername_pythonanywhere_com_wsgi.py`) and replace its contents with the snippet below.

WSGI snippet (paste into your PA WSGI file):

```python
import os
import sys
project_home = '/home/yourusername/site'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Activate virtualenv
activate_this = '/home/yourusername/.virtualenvs/restaurant-env/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), dict(__file__=activate_this))

# Optionally load .env file from project root (if you use .env)
env_path = os.path.join(project_home, '.env')
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                k,v = line.strip().split('=',1)
                os.environ.setdefault(k, v)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

5) Static files configuration (Web tab > Static files)
- Map `/static/` -> `/home/yourusername/site/staticfiles`
- Map `/media/` -> `/home/yourusername/site/media`

6) Database migration & collectstatic
Open Bash console on PA and run:
```bash
cd ~/site
source ~/.virtualenvs/restaurant-env/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

7) Reload web app
- In Web tab click "Reload".

8) Test
- Visit the site URL (the PA assigned or your custom domain) and test: signup, login, add-to-cart, upload media (if allowed), and admin.

Notes & tips
- If you use SQLite, it works for small sites but consider external Postgres for production.
- For email in PA, set SMTP env vars; the console backend is not usable in production.
- For payment webhooks, ensure your site is reachable publicly (use custom domain for stable URL) and configure webhook URL in the payment dashboard.

If you'd like, I can:
- Create a ready `.env.example` (done) and this README (done).
- Update `settings.py` to parse `DATABASE_URL` (requires adding `dj-database-url` to `requirements.txt`).
- Produce a short checklist of post-deployment tests.

Troubleshooting — ModuleNotFoundError: No module named 'Ong.settings'

If you see an error in the PA error log like:

```
ModuleNotFoundError: No module named 'Ong.settings'
```

It means the WSGI file or the `DJANGO_SETTINGS_MODULE` value on PythonAnywhere is pointing to `Ong.settings` while this project uses the package name `restaurantsaas` (the settings file is `restaurantsaas/settings.py`). Fix it by editing your PA WSGI file and ensuring the correct project path and settings module are used.

Example WSGI snippet to paste into `/var/www/yourusername_pythonanywhere_com_wsgi.py` (replace `yourusername` and paths):

```python
import os
import sys
project_home = '/home/david0011/Ong'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Ensure this matches the actual package that contains settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurantsaas.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Quick verification steps on PythonAnywhere (Bash console):

```bash
cd ~/Ong
source myvenv/bin/activate   # or the path to your virtualenv
python manage.py check
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

After that, reload the web app in the Web tab and re-check the error log. If you want, I can update this README further or prepare an exact, copy-paste WSGI file using your PythonAnywhere username and virtualenv path — tell me the username and venv path and I'll patch it for you.

