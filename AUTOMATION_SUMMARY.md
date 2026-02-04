# MPART @ UIS Automation Summary

## ✅ Tasks Completed

### ✅ Task 1: GitHub Actions Workflow

**File:** `.github/workflows/daily_mpart_scout.yml`

**Features:**
- ⏰ **Schedule:** Runs daily at 11:00 UTC (6:00 AM CST)
- 🖱️ **Manual Trigger:** `workflow_dispatch` for on-demand runs
- 🔐 **Secrets:** Injects `DATA_GOV_API_KEY` from GitHub Secrets
- 💾 **Auto-Commit:** Commits new matches back to repo automatically

**Workflow Steps:**
1. Checkout code
2. Set up Python 3.11
3. Install dependencies (Playwright, requests, etc.)
4. Install Playwright Chromium browser
5. Run `python src/scout_il.py --live`
6. Check if `data/mpart_matches.json` was updated
7. If changes found: Commit and push with timestamp
8. Upload artifacts for 30-day retention

**Required GitHub Secret:**
```
Settings → Secrets and variables → Actions → New repository secret
Name: DATA_GOV_API_KEY
Value: your_sam_gov_api_key_here
```

### ✅ Task 2: README Dashboard

**File:** `README.md` (Status Dashboard section)

**Added Sections:**
- 🔴 **Live Grant Matches** - Links to latest mpart_matches.json
- 🚀 **For Student Workers** - Quick command to run briefing script
- 🤖 **Automation Status** - GitHub Actions badge and workflow info
- 📁 **Key Files** - Reference table for all data files

### ✅ Bonus: Student Briefing Script

**File:** `src/student_briefing.py`

**Features:**
- 📊 Visual summary of latest matches
- 🎯 High priority matches highlighted (Score > 80)
- 📋 Mercenary lead assignments with icons
- 📅 Formatted deadlines
- 📝 Next steps guide for students

## Quick Reference

### For Students

```bash
# View latest matches
python3 src/student_briefing.py

# Or view raw JSON
cat data/mpart_matches.json | python3 -m json.tool
```

### For Administrators

```bash
# Manual trigger via GitHub
# → Actions tab → Daily MPART Grant Scout → Run workflow

# Set API key
export DATA_GOV_API_KEY="your_key"
python3 src/scout_il.py --live
```

## Files Created/Modified

| File | Description |
|------|-------------|
| `.github/workflows/daily_mpart_scout.yml` | GitHub Actions workflow for daily automation |
| `README.md` | Updated with Status Dashboard section |
| `src/student_briefing.py` | Student-friendly match viewer |
| `AUTOMATION_SUMMARY.md` | This documentation file |

## GitHub Actions Workflow Diagram

```
Daily at 6:00 AM CST
        │
        ▼
┌─────────────────────┐
│  GitHub Actions     │
│  Runner (Ubuntu)    │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌─────────┐  ┌──────────┐
│ Install │  │ Install  │
│ Python  │  │ Playwright│
└────┬────┘  └────┬─────┘
     │            │
     └──────┬─────┘
            ▼
┌─────────────────────┐
│  Run scout_il.py    │
│  --live             │
│                     │
│  • Scrape GATA      │
│  • Query SAM.gov    │
│  • Apply filters    │
│  • Score matches    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  New matches?       │
└──────────┬──────────┘
           │
     ┌─────┴─────┐
     ▼           ▼
┌────────┐  ┌──────────┐
│  YES   │  │    NO    │
│ Commit │  │   Skip   │
│ & Push │  │          │
└────┬───┘  └──────────┘
     │
     ▼
┌─────────────────────┐
│  Students see       │
│  updated matches    │
│  in repo            │
└─────────────────────┘
```

## Setup Checklist

- [ ] Add `DATA_GOV_API_KEY` to GitHub Secrets
- [ ] Test manual workflow run
- [ ] Verify student workers have repo access
- [ ] Document `student_briefing.py` in team onboarding
- [ ] Set up notifications (optional Slack/Discord webhook)

## Expected Output

When the workflow runs successfully, students will see:

```
🤖 Daily Scout: Found 5 MPART matches on 2026-02-04 11:00 UTC

- Automated grant discovery from Illinois GATA and SAM.gov
- Pre-filtered for Illinois Higher Education eligibility
- High-score matches (>80) flagged for DeepResearch

Workflow: Daily MPART Grant Scout
Run: 42
```

And the commit will appear in the repo history with updated JSON files.
