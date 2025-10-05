web: python3 -m gunicorn cinema_project.wsgi --bind 0.0.0.0:$PORT --workers 3 --log-file -
```)

4. **Save** and **redeploy** (or trigger a redeploy). This will avoid any `python` calls during startup.

5. Now run your migrations & collectstatic once (via Run Command):
   - Use the Railway **Run Command** (three-dots → Run Command) and paste:

```bash
python3 manage.py migrate
python3 manage.py collectstatic --noinput
