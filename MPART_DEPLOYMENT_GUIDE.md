# MPART @ UIS Deployment Guide

Complete setup and deployment instructions for the enhanced Grant Match system.

---

## Quick Start

```bash
# 1. Clone repository
git clone https://github.com/your-org/grant-match.git
cd grant-match

# 2. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Run discovery
python src/scout_il.py --live

# 5. View results
python src/student_briefing_v2.py
```

---

## Detailed Setup

### 1. Environment Setup

Create `.env` file:

```bash
# Required API Keys
DATA_GOV_API_KEY=your_sam_gov_api_key_here

# Email Configuration (optional)
SMTP_HOST=smtp.uis.edu
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
FROM_ADDRESS=mpart-grants@uis.edu
TO_ADDRESSES=lead1@uis.edu,lead2@uis.edu

# Notification Settings
SEND_DAILY_DIGEST=true
SEND_IMMEDIATE_ALERTS=false
HIGH_PRIORITY_THRESHOLD=80

# For testing without email
CONSOLE_EMAIL=true
```

### 2. GitHub Actions Setup

Configure repository secrets:

1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:

| Secret | Description |
|--------|-------------|
| `DATA_GOV_API_KEY` | SAM.gov API key |
| `SMTP_HOST` | Email server hostname |
| `SMTP_PORT` | Email server port |
| `SMTP_USERNAME` | Email username |
| `SMTP_PASSWORD` | Email password |
| `FROM_ADDRESS` | Sender email address |
| `TO_ADDRESSES` | Comma-separated recipient emails |

### 3. Web Dashboard Deployment

#### Option A: Streamlit Cloud (Free)

```bash
# 1. Push to GitHub
git push origin main

# 2. Go to https://streamlit.io/cloud
# 3. Connect your GitHub repository
# 4. Select src/dashboard/app.py as entry point
# 5. Deploy
```

#### Option B: Local/Server

```bash
# Run locally
streamlit run src/dashboard/app.py

# Or with custom port
streamlit run src/dashboard/app.py --server.port 8080
```

---

## Features Reference

### Email Notifications

**Daily Digest:**
- Sent automatically via GitHub Actions
- Includes high-priority matches (score ≥80)
- HTML and plain text formats

**Manual Send:**
```bash
python -c "
import sys; sys.path.insert(0, 'src')
from notifications.email_notifier import EmailNotifier
import json

with open('data/mpart_matches.json') as f:
    data = json.load(f)

notifier = EmailNotifier()
notifier.send_digest(data['matches'], data['summary'])
"
```

### Excel Export

```bash
# Generate Excel file
python -c "
import sys; sys.path.insert(0, 'src')
from export.excel_exporter import export_matches_to_excel
export_matches_to_excel()
"
```

**Excel Features:**
- Summary sheet with statistics
- Matches sheet with color-coded priorities
- Analytics sheet with charts
- Auto-sized columns
- Frozen header row

### Calendar Integration

```bash
# Generate calendar file
python -c "
import sys; sys.path.insert(0, 'src')
from integrations.calendar import generate_deadline_calendar
generate_deadline_calendar()
"
```

**Import to:**
- Google Calendar: Import .ics file
- Outlook: Open .ics file
- Apple Calendar: Double-click .ics file

### Decision Tracking

```python
# Example: Track a grant decision
from tracking import DecisionTracker, DecisionStatus

tracker = DecisionTracker()

# Mark as pursuing
tracker.update_status('GRANT-001', DecisionStatus.PURSUING, 
                     decided_by='Dr. Smith')

# Record submission
tracker.record_submission('GRANT-001')

# Record outcome
tracker.record_outcome('GRANT-001', awarded=True, amount='$50,000')

# Get analytics
print(tracker.get_win_rate())
```

### REST API

```bash
# Start API server
python -m uvicorn src.api.server:app --reload

# Endpoints:
# GET  /                    API info
# GET  /matches            List matches
# GET  /matches/{id}       Get specific match
# GET  /decisions          List decisions
# POST /decisions/{id}     Update decision
# GET  /analytics          Get analytics
# POST /export             Export data
# GET  /calendar/deadlines.ics  Calendar file
```

---

## Usage Workflows

### Daily Workflow (Students)

```bash
# 1. Check email for digest (automatic)

# 2. Or run briefing manually
python src/student_briefing_v2.py

# 3. Or view web dashboard
streamlit run src/dashboard/app.py

# 4. Update decision status
python -c "
import sys; sys.path.insert(0, 'src')
from tracking import DecisionTracker, DecisionStatus
tracker = DecisionTracker()
tracker.update_status('GRANT-001', DecisionStatus.PURSUING)
"

# 5. Export for sharing
python src/student_briefing_v2.py --excel
```

### Weekly Workflow (Faculty)

```bash
# 1. Review all high-priority matches
python src/student_briefing_v2.py --min-score 80

# 2. Check win rates and analytics
python -c "
import sys; sys.path.insert(0, 'src')
from tracking import DecisionTracker
tracker = DecisionTracker()
print(tracker.get_analytics())
"

# 3. Generate calendar for planning
python src/student_briefing_v2.py --calendar

# 4. Review team assignments
python src/student_briefing_v2.py --status pursuing
```

---

## Configuration

### Keyword Weights

Edit `config/settings.py` or use admin interface:

```python
from config import load_settings

settings = load_settings()
settings.update_keywords(
    medicaid=40,  # Increase weight
    rural_health=20
)
```

### Data Sources

Enable/disable sources:

```python
settings = load_settings()
settings.update_sources(
    rwjf=True,              # Robert Wood Johnson Foundation
    commonwealth_fund=True, # Commonwealth Fund
    academy_health=True,    # AcademyHealth
    cms_innovation=True     # CMS Innovation Center
)
```

---

## Troubleshooting

### Common Issues

**Issue: Playwright not found**
```bash
pip install playwright
playwright install chromium
```

**Issue: Email not sending**
- Check SMTP credentials in `.env`
- Verify `TO_ADDRESSES` is set
- Check spam folders
- Use `CONSOLE_EMAIL=true` for testing

**Issue: Excel export fails**
```bash
pip install pandas openpyxl
```

**Issue: No matches found**
- Verify `DATA_GOV_API_KEY` is set
- Check internet connection
- Verify GATA portal accessibility

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python src/scout_il.py --live
```

---

## Maintenance

### Regular Tasks

| Task | Frequency | Command |
|------|-----------|---------|
| Review keyword weights | Monthly | Edit config/settings.py |
| Clean old artifacts | Weekly | `find data -name "*.json" -mtime +30 -delete` |
| Update dependencies | Monthly | `pip install -U -r requirements.txt` |
| Backup decisions | Weekly | `cp data/grant_decisions.json backup/` |

### Updating

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt
playwright install chromium

# Verify installation
python src/scout_il.py --test
```

---

## Support

**Documentation:**
- README.md - Overview
- MPART_DEPLOYMENT_GUIDE.md - This file
- src/*/README.md - Module-specific docs

**Issue Reporting:**
Create GitHub issue with:
1. Error message
2. Steps to reproduce
3. Environment info (`python --version`, OS)

---

## Architecture Overview

```
grant-match/
├── src/
│   ├── scout_il.py              # Main discovery pipeline
│   ├── mpart_adapter.py         # MPART-specific matching
│   ├── notifications/           # Email system
│   │   ├── email_notifier.py
│   │   └── digest_generator.py
│   ├── dashboard/               # Web interface
│   │   └── app.py
│   ├── export/                  # Export modules
│   │   ├── excel_exporter.py
│   │   └── csv_exporter.py
│   ├── sources/                 # Grant sources
│   │   ├── rwjf.py
│   │   ├── commonwealth.py
│   │   ├── academyhealth.py
│   │   └── multistate.py
│   ├── tracking/                # Decision tracking
│   │   └── decision_tracker.py
│   ├── integrations/            # Calendar/CRM
│   │   └── calendar.py
│   └── api/                     # REST API
│       └── server.py
├── config/                      # Configuration
│   └── settings.py
├── data/                        # Data files
├── .github/workflows/           # CI/CD
└── docs/                        # Documentation
```

---

**Version:** 2.0  
**Last Updated:** 2026-02-04
