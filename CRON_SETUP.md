# Cron Job Examples for FUB to Sierra Converter

## File Cleanup (Run every hour)
```bash
# Edit crontab
crontab -e

# Add this line to run cleanup every hour
0 * * * * cd /path/to/FUB-to-Sierra-CSV-Converter/web_app && /path/to/python cleanup.py >> /path/to/logs/cleanup.log 2>&1
```

## Example with virtual environment
```bash
# Run cleanup every hour at minute 0
0 * * * * cd /path/to/FUB-to-Sierra-CSV-Converter && /path/to/venv/bin/python web_app/cleanup.py >> logs/cleanup.log 2>&1
```

## Run cleanup every 30 minutes (more aggressive)
```bash
*/30 * * * * cd /path/to/FUB-to-Sierra-CSV-Converter && /path/to/venv/bin/python web_app/cleanup.py >> logs/cleanup.log 2>&1
```

## Run cleanup daily at 2 AM
```bash
0 2 * * * cd /path/to/FUB-to-Sierra-CSV-Converter && /path/to/venv/bin/python web_app/cleanup.py >> logs/cleanup.log 2>&1
```

## Monitor disk space and alert if low
```bash
# Check every 6 hours
0 */6 * * * df -h /path/to/FUB-to-Sierra-CSV-Converter | awk 'NR==2 {if(substr($5,1,length($5)-1) > 80) print "Disk usage high: " $5}' | mail -s "Disk Alert" your@email.com
```

## Verify cron jobs are running
```bash
# View current cron jobs
crontab -l

# View cron log (location varies by system)
tail -f /var/log/cron
# or
tail -f /var/log/syslog | grep CRON
```

## Manual Cleanup
```bash
# Run cleanup manually
cd /path/to/FUB-to-Sierra-CSV-Converter
python web_app/cleanup.py

# Or with virtual environment
cd /path/to/FUB-to-Sierra-CSV-Converter
source venv/bin/activate
python web_app/cleanup.py
```

## Systemd Timer (Alternative to Cron)

Create `/etc/systemd/system/fub-cleanup.service`:
```ini
[Unit]
Description=FUB Converter File Cleanup

[Service]
Type=oneshot
User=www-data
WorkingDirectory=/path/to/FUB-to-Sierra-CSV-Converter
ExecStart=/path/to/venv/bin/python web_app/cleanup.py
```

Create `/etc/systemd/system/fub-cleanup.timer`:
```ini
[Unit]
Description=Run FUB Converter cleanup hourly

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl enable fub-cleanup.timer
sudo systemctl start fub-cleanup.timer
sudo systemctl status fub-cleanup.timer
```
