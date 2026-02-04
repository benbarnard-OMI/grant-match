# Grant Match - AI Coding Agent Guide

> Comprehensive guide for AI coding agents working on the Grant Match project.

---

## Project Overview

**Grant Match** is an AI-powered grant matching and discovery system. While originally designed to match Vanderbilt University faculty with funding opportunities, the project has evolved to focus on automated grant scouting for **MPART @ UIS** (Medical Policy Applied Research Team at University of Illinois Springfield).

### Current Focus: MPART @ UIS Grant Scout

The system now operates as a daily automated pipeline that:
1. Scrapes the Illinois GATA (Grant Accountability and Transparency Act) portal
2. Queries the SAM.gov federal opportunities API
3. Scores opportunities against MPART research pillars
4. Assigns recommended leads ("Mercenary" profiles)
5. Triggers DeepResearch for high-scoring matches (>80)

### Core Value Proposition

The system doesn't just find matches—it explains **WHY** each match makes sense with specific references to MPART's research focus areas:
- PolicyDelta - State policy variation analysis
- National Policy Tracker implementation
- Regulatory Monitoring systems
- Healthcare Infrastructure evaluation
- 1115 Waiver technical assistance

---

## Project Status

**Current Phase:** Live automated ingestion with MPART @ UIS

**Active Components:**
- ✅ Daily automated grant scouting (GitHub Actions)
- ✅ Illinois GATA portal web scraping
- ✅ SAM.gov API integration
- ✅ Heuristic keyword scoring
- ✅ Mercenary lead assignment system
- ✅ Student briefing interface
- ⏳ DeepResearch AI integration (skeleton implemented)

---

## Technology Stack

### Core Technologies

| Category | Technology | Purpose |
|----------|------------|---------|
| Language | Python 3.11+ | Primary development language |
| Web Automation | Playwright | JavaScript-rendered page scraping |
| HTTP Requests | requests | API calls (SAM.gov) |
| Scheduling | GitHub Actions | Daily automation (cron) |
| Data Storage | JSON files | Structured data storage |

### Python Dependencies

```
playwright              # Web browser automation
requests                # HTTP requests for APIs
beautifulsoup4          # HTML parsing
lxml                    # XML/HTML parser
trafilatura             # Content extraction
```

### Environment Variables

Required for live API access:
```bash
DATA_GOV_API_KEY        # For SAM.gov API access
```

---

## Project Structure

```
grant-match/
├── src/                           # Source code
│   ├── scout_il.py               # Main grant discovery pipeline
│   ├── mpart_adapter.py          # MPART-specific matching logic
│   ├── run_live_demo.py          # Demo mode with mock data
│   ├── student_briefing.py       # Student-friendly match viewer
│   └── data_collection/          # Legacy Vanderbilt faculty scrapers
│       ├── README.md
│       ├── scrape_faculty_listings.py
│       └── scrape_faculty_websites.py
│
├── data/                          # JSON data files
│   ├── department_inventory.json # Department metadata
│   ├── faculty_from_fis.json     # MPART team + Mercenary profiles
│   ├── mpart_matches.json        # Latest grant match results
│   ├── live_ingestion_results.json # Pipeline execution results
│   └── gata_live_capture.json    # Raw scraped GATA data
│
├── .github/workflows/             # CI/CD automation
│   └── daily_mpart_scout.yml     # Daily 6 AM CST execution
│
├── docs/                          # Documentation
│   ├── MCP_SETUP.md
│   ├── fis_data_analysis.md
│   └── web_scraping_findings.md
│
├── FIS_All_Tenured_TT.xlsx       # Source Excel file (legacy)
├── README.md                      # Project overview
└── AGENTS.md                      # This file
```

---

## Architecture

### Grant Discovery Pipeline (`scout_il.py`)

```
┌─────────────────┐     ┌─────────────────┐
│  GATAWebScraper │     │   SAMSource     │
│  (Playwright)   │     │  (SAM.gov API)  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌─────────────────────┐
         │ GrantDiscoveryPipeline
         │                     │
         │  1. Pre-filter      │
         │  2. Score (0-100)   │
         │  3. Trigger AI >80  │
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │  mpart_matches.json │
         └─────────────────────┘
```

### MPART Matching Adapter (`mpart_adapter.py`)

The adapter implements a tiered matching workflow:

1. **Pre-filtering** - Deterministic checks (deadline, eligibility)
2. **Heuristic Scoring** - Keyword-based matching (0-100 score)
3. **Deep Research** - AI analysis for high-scoring grants (>50)
4. **Mercenary Tagging** - Assign to specialized lead profiles

### Mercenary Lead System

Three specialized "Mercenary" profiles for lead assignment:

| Mercenary | Specialty | Keywords |
|-----------|-----------|----------|
| `mercenary_policy` | State Policy Expert | state policy, medicaid variations, 1115 waiver, regulatory analysis |
| `mercenary_data` | Data/AI Expert | policy monitoring, automated, ai-assisted, nlp, data pipeline |
| `mercenary_eval` | Rural/Eval Expert | rural health, infrastructure, government evaluation, health disparities |

---

## Build and Run Commands

### Local Development

```bash
# Install dependencies
pip install playwright requests beautifulsoup4 lxml
playwright install chromium

# Set API key (optional for demo mode)
export DATA_GOV_API_KEY="your_key_here"
```

### Running the Pipeline

```bash
# Run live ingestion (requires API key for SAM.gov)
python src/scout_il.py --live

# Run demo mode with mock data
python src/run_live_demo.py

# Test MPART adapter with sample grants
python src/mpart_adapter.py --test

# View student briefing
python src/student_briefing.py
```

### Manual Trigger via GitHub Actions

The workflow can be triggered manually from the GitHub Actions tab:
- Workflow: `Daily MPART Grant Scout`
- File: `.github/workflows/daily_mpart_scout.yml`

---

## Code Style Guidelines

### Python Style

- Use type hints for function signatures
- Follow PEP 8 naming conventions (snake_case)
- Use docstrings for all classes and functions
- Import ordering: stdlib, third-party, local

Example:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum


@dataclass
class GrantOpportunity:
    """Data class representing a grant opportunity."""
    id: str
    title: str
    agency: str
    description: str
    eligibility: str
    award_amount: Optional[str] = None
    deadline: Optional[datetime] = None
```

### Class Organization

1. Enums for status/funding source types
2. Data classes using `@dataclass`
3. Abstract base classes for extensibility
4. Concrete implementations

### Error Handling

- Use logging with appropriate levels
- Graceful degradation when APIs fail
- Continue processing on individual grant failures

Example:
```python
logger = logging.getLogger(__name__)

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"API request failed: {e}")
    return []
```

---

## Testing Strategy

### Manual Testing

The project uses manual testing through CLI interfaces:

```bash
# Test with sample data
python src/mpart_adapter.py --test

# Verify output files
python -m json.tool data/mpart_matches.json | less
```

### Test Data

Mock grant opportunities are embedded in `mpart_adapter.py` for testing:
- `IL-TRUTH-001` through `IL-REJECTED-005` - Illinois GATA scenarios
- `FED-REJECTED-006` - Federal scenario

### Quality Verification

Check these metrics in output files:
- Pre-filter pass rate (target: 30-50%)
- High-score matches >80 (target: 5-10%)
- Mercenary lead distribution (varies by grant mix)

---

## Security Considerations

### API Keys

- Store in environment variables only
- Never commit to git (see `.gitignore`)
- Use GitHub Secrets for Actions workflows

### Web Scraping Ethics

- Respect rate limits (2-3 seconds between requests)
- Use identifiable User-Agent strings
- Scrape during off-peak hours when possible

### Data Privacy

- Faculty profiles contain work information only
- Grant data is public information
- Output files are committed to repo (no PII)

---

## Key Data Files

### `data/faculty_from_fis.json`

Contains MPART team profile and Mercenary roster:
```json
{
  "faculty": [
    {
      "id": "mpart_uis_team_001",
      "name": "MPART @ UIS Research Team",
      "research_interests": ["Medicaid policy", "PolicyDelta", ...],
      "research_areas": ["health_policy", "policy_delta", ...]
    },
    {
      "id": "mercenary_policy",
      "name": "Policy Mercenary",
      "specialization_tags": ["policy", "regulatory", "waivers"]
    }
  ]
}
```

### `data/mpart_matches.json`

Output format for grant matches:
```json
{
  "metadata": {
    "generated_at": "2026-02-03T...",
    "organization": "MPART @ UIS"
  },
  "matches": [
    {
      "grant_id": "SAM-...",
      "grant_title": "...",
      "recommended_lead": "mercenary_policy",
      "match_score": 85,
      "keyword_score": 80,
      "research_depth": "deep_research",
      "rationale": "..."
    }
  ]
}
```

---

## Common Tasks

### Adding a New Grant Source

1. Create class extending `GrantSource` in `scout_il.py`:
```python
class NewSource(GrantSource):
    def __init__(self):
        super().__init__(name="New Source", base_url="https://...")
    
    def discover(self, filters=None) -> List[GrantOpportunity]:
        # Implementation
        pass
```

2. Register in pipeline:
```python
pipeline.register_source(NewSource())
```

### Modifying Keyword Weights

Edit `HeuristicScorer.KEYWORD_WEIGHTS` in `scout_il.py`:
```python
KEYWORD_WEIGHTS = {
    'medicaid': 35,
    'new_keyword': 20,
    ...
}
```

### Adding a Mercenary Profile

1. Add entry in `MPARTProfileLoader.MERCENARY_PROFILES` (mpart_adapter.py)
2. Add keywords in `MercenaryMatcher.MERCENARY_KEYWORDS`
3. Update `get_mercenary_name()` method
4. Update icon mapping in `student_briefing.py`

---

## Troubleshooting

### Playwright Not Working

```bash
# Verify installation
playwright install chromium

# Check browser binaries
python -c "from playwright.sync_api import sync_playwright; print('OK')"
```

### SAM.gov API Errors

- Verify `DATA_GOV_API_KEY` is set
- Check API rate limits (10 requests/minute for free tier)
- Review API documentation: https://open.gsa.gov/api/sam/opportunities/

### Import Errors

No known import issues at this time. If you see module import errors, verify
your `PYTHONPATH` includes `src/` or run scripts from the project root.

---

## Resources

### External APIs

- Illinois GATA Portal: https://omb.illinois.gov/public/gata/csfa/
- SAM.gov API: https://open.gsa.gov/api/sam/opportunities/
- Data.gov API Key: https://api.data.gov/signup/

### Documentation

- `README.md` - High-level project overview
- `DEMO_PLAN.md` - Demo preparation notes
- `PROGRESS_SUMMARY.md` - Development progress tracking
- `ISSUES_SUMMARY.md` - GitHub issues tracking

---

## Contact and Contribution

- **Repository:** https://github.com/vanderbilt-data-science/grant-match
- **Issues:** Track work via GitHub issues
- **Documentation:** Maintain in `/docs` directory

---

**Last Updated:** 2026-02-04
**Project Phase:** Live automated ingestion operational
**Next Milestone:** Implement DeepResearch AI integration
