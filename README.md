# Back-end-Development-Capstone

Django band website completed from IBM Skills Network's starter template. Includes songs with lyrics modals, photos, signup/login/logout, concert listings and per-user attendance changes, plus Django admin management of concerts.

## Environment Setup
- Repository created from the supplied template; course bootstrap script: bin/setup.sh.
- Verified using Python 3.10 in IBM Skills Network Labs in capstone-env.
- Install: python -m pip install -r requirements.txt
- Initialize: python manage.py migrate
- Verify: python manage.py test concert
- Start: python manage.py runserver 0.0.0.0:8000

Set SONGS_URL to the Songs service /song endpoint and PICTURES_URL to the Pictures service /picture endpoint. Without those variables, the local-development single-song and single-photo examples from Module 3 are used.

## Container and deployment
Dockerfile and entrypoint.sh run migrations before startup. Set DJANGO_SECRET_KEY and DJANGO_SUPERUSER_PASSWORD through the runtime environment or a Kubernetes Secret, never in Git. DJANGO_SUPERUSER_USERNAME defaults to admin. Configure DJANGO_ALLOWED_HOSTS for the deployment hostname. deployment.yml contains placeholders CAPSTONE_IMAGE, SONGS_ENDPOINT and PICTURES_ENDPOINT to fill with the actual lab resources before applying.

The app uses SQLite and the built-in Django User model. Test and demo data should contain no personal information.

## Admin setup and verification
For a local installation, run `python manage.py createsuperuser` after migrations and enter the username, email and password interactively. Start the server, open `/admin/`, and sign in with that account. Under Concert, choose Concerts > Add to create concert data; authenticated users can then view it at `/concerts/`.

For the verified Kubernetes deployment, `entrypoint.sh` created the `admin` superuser using `DJANGO_SUPERUSER_PASSWORD` supplied by the `capstone-config` Kubernetes Secret. The password is never stored in this repository. Successful admin login and creation of the Djirection Winter Tour concert were verified in the deployed application.
