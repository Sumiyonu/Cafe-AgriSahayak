# 🌐 Production Deployment Guide

This guide covers deploying the Café Management System to production environments.

## 1. Environment Variables
Ensure the following variables are set in your production environment:
- `MONGO_URI`: Remote MongoDB connection string (e.g., MongoDB Atlas).
- `FLASK_ENV`: Set to `production`.
- `DEBUG`: Set to `False`.

## 2. Local Network Deployment
To allow other devices on your network to access the dashboard:
1. Update `app.py` to run on `0.0.0.0`:
   ```python
   app.run(host='0.0.0.0', port=5000)
   ```
2. Find your local IP (e.g., 192.168.1.5).
3. Access from other devices via `http://192.168.1.5:5000`.

## 3. Cloud Deployment (Heroku Example)
1. Create a `Procfile`: `web: gunicorn app:app`
2. Add `gunicorn` to `requirements.txt`.
3. Push to Heroku: `git push heroku main`
4. Set Config Vars in Heroku dashboard.

## 4. Docker Containerization
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "app.py"]
```

## 5. Security Best Practices
- **Enable SSL**: Use HTTPS for all connections.
- **Authentication**: Add a login layer to the dashboard.
- **Rate Limiting**: Use Flask-Limiter for API protection.
- **Database Backup**: Schedule regular MongoDB dumps.

---
For specific deployment support, consult the documentation of your hosting provider.
