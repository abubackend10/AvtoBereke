# Deployment

## Render deployment

The repository includes a Render Blueprint at `render.yaml`. It creates the
web service; create a persistent Render PostgreSQL database separately, then
provide its **Internal Database URL** as `DATABASE_URL` when configuring the
Blueprint. Set `CLOUDINARY_URL` from Cloudinary as a secret when prompted.
Never commit either value or put them in the repository.

The Blueprint builds static assets, applies database migrations, creates the
deployment superuser if it does not already exist, and starts Gunicorn on
Render's assigned port. Set `DJANGO_SUPERUSER_USERNAME`,
`DJANGO_SUPERUSER_EMAIL`, and `DJANGO_SUPERUSER_PASSWORD` as private Render
environment variables. Use a unique, strong password and do not commit any of
these values. The admin page is available at `https://<your-domain>/admin/`.
The project does not import local SQLite data; add site content through the
live admin after deployment. The Render web plan is configured as free; choose
the database plan deliberately and review its cost and retention policy before
creating it.

Uploaded photos live in Cloudinary, not on the Render web service's filesystem.

## Linux deployment

These files target a Linux server running systemd, Nginx, and PostgreSQL. The
application's production settings require `SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`,
a persistent `DATABASE_URL`, `CLOUDINARY_URL`, and the three
`DJANGO_SUPERUSER_*` variables. The admin URL is
`https://<your-domain>/admin/`. The systemd unit explicitly selects
`core.settings.production` and creates the superuser before starting Gunicorn.

## Install

1. Point the domain's DNS records to the server, then install Nginx and Python
   venv support and create the application account:

   ```sh
   sudo apt update
   sudo apt install nginx python3-venv
   sudo adduser --system --group --home /srv/avtobereke avtobereke
   ```

2. Create a Cloudinary account and copy its `CLOUDINARY_URL` from the API Keys
   page. Keep the value private; do not commit it to the repository. Deploy the
   repository to `/srv/avtobereke/current`. Create a Python virtual environment
   at `/srv/avtobereke/venv` and install `requirements.txt`.
3. Before the first deployment, make the local database and `back_media`
   directory available in the project checkout. Set `CLOUDINARY_URL` in that
   shell and run `python manage.py migrate_media_to_cloudinary`. The command
   uploads existing site and car photos, updates their stored names, and keeps
   the local originals. If it reports a missing file or upload error, stop and
   resolve that before deploying.
4. Copy `deploy/avtobereke.env.example` to
   `/etc/avtobereke/avtobereke.env`. Set a unique `SECRET_KEY`, the real
   domain(s), PostgreSQL connection details, `CLOUDINARY_URL`, and unique
   `DJANGO_SUPERUSER_*` values. URL-encode special characters in database
   credentials. Restrict the file to root and the application group, for
   example `root:www-data` with mode `640`.
5. Apply migrations and collect static files. Ensure the application user owns
   the deployed source and can write to `back_static`, then run:

   ```sh
   sudo systemd-run --wait --pipe --uid=avtobereke --gid=www-data \
     --property=EnvironmentFile=/etc/avtobereke/avtobereke.env \
     --working-directory=/srv/avtobereke/current \
     /srv/avtobereke/venv/bin/python manage.py migrate --noinput
   sudo systemd-run --wait --pipe --uid=avtobereke --gid=www-data \
     --property=EnvironmentFile=/etc/avtobereke/avtobereke.env \
     --working-directory=/srv/avtobereke/current \
     /srv/avtobereke/venv/bin/python manage.py collectstatic --noinput
   ```
6. Install `deploy/systemd/avtobereke.service` as
   `/etc/systemd/system/avtobereke.service`. Install
   `deploy/nginx/avtobereke.conf` as
   `/etc/nginx/sites-available/avtobereke`, replace the example domains, and
   enable the site:

   ```sh
   sudo ln -s /etc/nginx/sites-available/avtobereke /etc/nginx/sites-enabled/avtobereke
   sudo systemctl daemon-reload
   sudo nginx -t
   sudo systemctl enable --now avtobereke
   sudo systemctl reload nginx
   ```

7. Configure HTTPS with Let's Encrypt after Nginx is serving the domain, for
   example with `sudo certbot --nginx -d example.com -d www.example.com`.
   Verify certificate renewal is enabled and test the site over HTTPS.

New JPEG, PNG, and WebP uploads are resized to at most 1920x1920 and compressed
before being sent to Cloudinary. Catalog images are already lazy-loaded by the
browser. Deleting a car removes its unreferenced main and gallery images from
Cloudinary after the database transaction succeeds. Gunicorn listens only on
loopback; external HTTP traffic goes through Nginx.
The default is three Gunicorn workers with two threads each. Adjust
`WEB_CONCURRENCY` to the server's CPU and memory after load testing: 2,000–3,000
registered visitors do not imply that many simultaneous requests. Use
PostgreSQL rather than SQLite in production.
