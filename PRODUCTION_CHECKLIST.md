# Production Deployment Checklist

## ✅ Completed Items

### Security
- [x] Secret key using environment variable
- [x] .env file excluded from git
- [x] File upload size limits (50MB)
- [x] Secure filename handling
- [x] CSRF protection via Flask sessions

### UI/UX
- [x] Favicon added
- [x] Responsive design
- [x] Dark/Light theme toggle
- [x] Navigation protection (warns before leaving with unsaved files)
- [x] Browser reload warning
- [x] Session cleared on reload with user notification
- [x] Material Design components
- [x] Preview with zoom controls
- [x] Resizable table columns
- [x] Copy/paste protection on preview

### Functionality
- [x] Column mapping UI
- [x] CSV conversion with validation
- [x] File chunking (5000 rows per file)
- [x] ZIP download for multiple files
- [x] Preview (100 rows)
- [x] Conversion log with detailed output
- [x] Payment integration ready
- [x] Session management

### Files & Structure
- [x] requirements.txt present
- [x] .gitignore configured
- [x] Environment variable example (.env.example)
- [x] Upload/download folders auto-created

## ⚠️ Action Required Before Production

### Critical Security
1. **Change DEBUG mode**
   - File: `web_app/app.py` line 701
   - Change: `app.run(debug=True, ...)` → `app.run(debug=False, ...)`
   - Or better: Use production WSGI server (see below)

2. **Set Production SECRET_KEY**
   - Create `.env` file in `web_app/` folder
   - Add: `SECRET_KEY=your-secure-random-key-here`
   - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

3. **Configure Payment Link**
   - Add to `.env`: `PAYMENT_LINK=https://your-stripe-payment-link`
   - Add to `.env`: `STRIPE_WEBHOOK_SECRET=whsec_...`

### Production Server Setup
4. **Use Production WSGI Server**
   ```bash
   # Install gunicorn
   pip install gunicorn
   
   # Run with gunicorn instead of Flask dev server
   gunicorn -w 4 -b 0.0.0.0:5001 web_app.app:app
   ```

5. **Add gunicorn to requirements.txt**
   ```
   gunicorn==21.2.0
   ```

### Performance & Reliability
6. **Configure File Cleanup**
   - Add scheduled task to clean old uploads/downloads
   - Suggestion: Cron job or background worker to delete files older than 1 hour

7. **Add Error Logging**
   - Configure Flask logging to file
   - Consider using services like Sentry for error tracking

8. **Set Up Reverse Proxy**
   - Use Nginx or Apache in front of gunicorn
   - Handle SSL/TLS certificates
   - Configure static file serving

### Optional Improvements
9. **Add Rate Limiting**
   - Install: `Flask-Limiter`
   - Prevent abuse

10. **Add File Validation**
    - Verify CSV format before processing
    - Add virus scanning for uploaded files

11. **Database for Analytics** (optional)
    - Track conversion stats
    - Monitor usage patterns

12. **Backup Strategy**
    - Regular database backups (if using DB)
    - Monitor disk space for uploads/downloads

## Environment Variables Template

Create `web_app/.env` file:
```
SECRET_KEY=your-secure-random-key-here
PAYMENT_LINK=https://buy.stripe.com/your-payment-link
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

## Deployment Commands

### Option 1: Simple Production Run
```bash
cd /path/to/FUB-to-Sierra-CSV-Converter
source venv/bin/activate  # if using virtual env
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5001 web_app.app:app
```

### Option 2: Systemd Service (Linux)
Create `/etc/systemd/system/fub-converter.service`:
```ini
[Unit]
Description=FUB to Sierra CSV Converter
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/FUB-to-Sierra-CSV-Converter
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5001 web_app.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Option 3: Docker (create Dockerfile)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "web_app.app:app"]
```

## Testing Before Production
- [ ] Test with large CSV files (>10,000 rows)
- [ ] Test payment flow end-to-end
- [ ] Test on different browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile devices
- [ ] Verify file cleanup works
- [ ] Load testing with multiple concurrent users

## Monitoring
- Monitor disk space (uploads/downloads folders)
- Monitor memory usage
- Monitor response times
- Set up uptime monitoring (UptimeRobot, Pingdom, etc.)
- Monitor error rates

## Support Email
Update in footer: `support@example.com` → your actual support email
