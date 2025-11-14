# Quick Deployment Guide

## ✅ Production Checklist Complete!

All critical items have been addressed. Here's your deployment summary:

## What Was Added

### 1. Security & Configuration
- ✅ Debug mode controlled by environment variable
- ✅ `.env.example` file with all required variables
- ✅ Logging directory added to `.gitignore`

### 2. Production Features
- ✅ **Health Check Endpoint**: `/health` for monitoring
- ✅ **Error Logging**: Rotating log files in `logs/` directory
- ✅ **File Cleanup Script**: `web_app/cleanup.py` for automated cleanup
- ✅ **Gunicorn**: Added to requirements.txt

### 3. Documentation
- ✅ `PRODUCTION_CHECKLIST.md` - Full production guidelines
- ✅ `CRON_SETUP.md` - Automated cleanup instructions
- ✅ This deployment guide

## Quick Start Deployment

### Step 1: Environment Setup
```bash
cd /path/to/FUB-to-Sierra-CSV-Converter

# Create .env file
cp web_app/.env.example web_app/.env

# Edit .env with your values
nano web_app/.env
```

Required environment variables:
```env
SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
PAYMENT_LINK=https://buy.stripe.com/your-payment-link
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
FLASK_DEBUG=false  # Important for production!
```

### Step 2: Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Run Production Server
```bash
# Development (for testing)
python web_app/app.py

# Production with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 web_app.app:app

# Production with access logs
gunicorn -w 4 -b 0.0.0.0:5001 --access-logfile logs/access.log --error-logfile logs/error.log web_app.app:app
```

### Step 4: Setup File Cleanup
```bash
# Test cleanup script
python web_app/cleanup.py

# Setup hourly cron job
crontab -e
# Add: 0 * * * * cd /path/to/FUB-to-Sierra-CSV-Converter && /path/to/venv/bin/python web_app/cleanup.py >> logs/cleanup.log 2>&1
```

### Step 5: Verify Deployment
```bash
# Check health endpoint
curl http://localhost:5001/health

# Test file upload
# Open browser to http://localhost:5001
```

## Nginx Reverse Proxy (Recommended)

Create `/etc/nginx/sites-available/fub-converter`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Static files
    location /static {
        alias /path/to/FUB-to-Sierra-CSV-Converter/web_app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # File upload settings
        client_max_body_size 50M;
        proxy_read_timeout 300s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/fub-converter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Systemd Service (Auto-restart)

Create `/etc/systemd/system/fub-converter.service`:
```ini
[Unit]
Description=FUB to Sierra CSV Converter
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/FUB-to-Sierra-CSV-Converter
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 --access-logfile logs/access.log --error-logfile logs/error.log web_app.app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fub-converter
sudo systemctl start fub-converter
sudo systemctl status fub-converter

# View logs
sudo journalctl -u fub-converter -f
```

## SSL Certificate (Let's Encrypt)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (usually automatic, but verify)
sudo certbot renew --dry-run
```

## Monitoring & Maintenance

### Check Health
```bash
# Application health
curl https://your-domain.com/health

# Server status
sudo systemctl status fub-converter
sudo systemctl status nginx

# View logs
tail -f logs/fub_converter.log
tail -f logs/access.log
tail -f logs/error.log
tail -f logs/cleanup.log
```

### Disk Usage
```bash
# Check disk space
df -h

# Check upload/download folders
du -sh web_app/uploads/
du -sh web_app/downloads/

# Check logs size
du -sh logs/
```

### Performance Tuning
```bash
# Gunicorn workers formula: (2 * CPU cores) + 1
# For 4 cores: -w 9

# Monitor memory
htop
free -h

# Monitor processes
ps aux | grep gunicorn
```

## Backup Strategy

### Application Files
```bash
# Backup entire application
tar -czf fub-converter-backup-$(date +%Y%m%d).tar.gz \
  --exclude='web_app/uploads/*' \
  --exclude='web_app/downloads/*' \
  --exclude='logs/*' \
  --exclude='venv/*' \
  /path/to/FUB-to-Sierra-CSV-Converter
```

### Database Backup (if using database)
```bash
# Not applicable currently - no database
# Files are session-only and automatically cleaned
```

## Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u fub-converter -n 50

# Check port
sudo netstat -tlnp | grep 5001

# Test gunicorn manually
cd /path/to/FUB-to-Sierra-CSV-Converter
source venv/bin/activate
gunicorn -w 1 -b 127.0.0.1:5001 web_app.app:app
```

### High disk usage
```bash
# Run cleanup manually
python web_app/cleanup.py

# Check cron job
crontab -l
sudo grep CRON /var/log/syslog

# Force cleanup (careful!)
rm -f web_app/uploads/*
rm -f web_app/downloads/*
```

### Permission errors
```bash
# Fix ownership
sudo chown -R www-data:www-data /path/to/FUB-to-Sierra-CSV-Converter

# Fix permissions
sudo chmod -R 755 /path/to/FUB-to-Sierra-CSV-Converter
sudo chmod -R 775 web_app/uploads web_app/downloads logs
```

## Security Checklist

- [ ] SECRET_KEY is strong and unique
- [ ] Debug mode is OFF (FLASK_DEBUG=false)
- [ ] SSL/TLS certificate installed
- [ ] Firewall configured (only ports 80, 443, 22 open)
- [ ] File upload limits enforced (50MB)
- [ ] Regular security updates: `sudo apt update && sudo apt upgrade`
- [ ] Monitoring enabled
- [ ] Backups configured

## Support

For issues or questions:
- Check logs first: `logs/fub_converter.log`
- Email: support@yourcompany.com (update this!)
- GitHub Issues: https://github.com/jsayram/FUB-to-Sierra-CSV-Converter/issues

## Update Procedure

```bash
cd /path/to/FUB-to-Sierra-CSV-Converter

# Backup first!
tar -czf backup-$(date +%Y%m%d).tar.gz .

# Pull latest code
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart service
sudo systemctl restart fub-converter

# Verify
curl https://your-domain.com/health
```

---

## 🚀 You're Ready for Production!

All critical items are complete. Follow the steps above to deploy securely.
