# Render.com Deployment Setup Guide

## Environment Variable Configuration

### Setting DATABASE_URL on Render.com

1. Go to your Render.com dashboard
2. Select your web service
3. Navigate to the **Environment** tab
4. Add a new environment variable:

   **Variable Name:** `DATABASE_URL`
   
   **Value:** `postgresql://test_postgres_3npm_user:2aZ22nTtxSmknxlltLTgl8dT0olAzgTw@dpg-d60u8rffte5s73bfsar0-a.oregon-postgres.render.com/test_postgres_3npm`

5. Click **Save Changes**

Render will automatically redeploy your application with the new environment variable.

### Additional Environment Variables

You may also want to set:

- `PORT` - Render automatically sets this, but you can override if needed (default: 10000)
- `FLASK_ENV` - Set to `production` for production deployments

## Render.com Start Command

In your Render.com web service settings, set the **Start Command** to:

```bash
gunicorn web_ui:app
```

Or for Python direct execution:

```bash
python web_ui.py
```

The application will automatically use the PORT environment variable that Render sets.

## How It Works

### In Your Code

The application now automatically reads the `DATABASE_URL` environment variable:

1. **config.py** - Reads `DATABASE_URL` from environment:
   ```python
   DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///profiles.db')
   ```

2. **database.py** - Automatically detects PostgreSQL vs SQLite:
   - If `DATABASE_URL` starts with `postgresql://` or `postgres://`, uses PostgreSQL
   - Otherwise, falls back to SQLite for local development
   
3. **web_ui.py** - Reads `PORT` from environment (Render sets this automatically)

### Local Development

For local development, you can:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your local database URL (or leave it for SQLite):
   ```
   DATABASE_URL=sqlite:///profiles.db
   ```

3. Install python-dotenv (optional):
   ```bash
   pip install python-dotenv
   ```

4. Load environment variables before running (optional):
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

Or simply run without `.env` and it will use SQLite by default.

## Database Migration

Since you're switching from SQLite to PostgreSQL, your database will start empty. You'll need to:

1. Recreate your profiles through the web UI, or
2. Export data from SQLite and import to PostgreSQL (manual process)

## Deployment Checklist

- [x] Added `psycopg2-binary` to requirements.txt
- [x] Updated `config.py` to read `DATABASE_URL` from environment
- [x] Updated `database.py` to support both PostgreSQL and SQLite
- [x] Updated `web_ui.py` to read `PORT` from environment
- [x] Created `.env.example` for reference
- [ ] Set `DATABASE_URL` environment variable on Render.com
- [ ] Push changes to your Git repository
- [ ] Render will automatically deploy the changes

## Testing

After deployment:

1. Check Render logs to ensure the application started successfully
2. Look for the database connection message in the logs
3. Access your web UI and try creating a profile
4. Verify the profile is saved in PostgreSQL

## Troubleshooting

### Connection Issues

If you get connection errors, verify:
- The DATABASE_URL is correct and complete
- The PostgreSQL instance is running on Render
- Network/firewall settings allow connections

### psycopg2 Errors

If you see "psycopg2 not installed" errors:
- Ensure `psycopg2-binary==2.9.9` is in your requirements.txt
- Check Render build logs to confirm it was installed

### SQLite Fallback

The application will automatically fall back to SQLite if:
- DATABASE_URL is not set, or
- DATABASE_URL doesn't start with postgresql:// or postgres://

This is useful for local development but won't persist data on Render (as the filesystem is ephemeral).
