# Grant Match - AI Coding Agent Guide

> Comprehensive guide for AI coding agents working on the Grant Match project.

---

## Project Overview

**Grant Match** is an AI-powered grant matching system that automatically connects Vanderbilt University faculty researchers with relevant funding opportunities through contextualized, personalized recommendations.

### Core Value Proposition

The system doesn't just find matches—it explains **WHY** each match makes sense with specific references to publications, prior work, and RFP requirements.

### Key Innovation

- Processes ALL 1000+ faculty per RFP (no pre-filtering)
- Generates specific rationales citing actual publications and RFP sections
- Cost-effective: ~$40-60 per RFP to analyze entire faculty population
- Feedback-driven continuous improvement

---

## Project Status

**Current Phase:** Data collection infrastructure complete, ready for profile generation

**Progress:** ~30% complete (5 of 16 GitHub issues)

**Completed:**
- ✓ MCP server setup (Playwright)
- ✓ Department structure mapping (8 departments)
- ✓ FIS faculty data extraction (110 faculty)
- ✓ Web scraping infrastructure (Issues #4-5 scripts ready)

**Pending:**
- ⏳ Execute web scraping scripts (requires Playwright MCP activation)
- ⏳ Publication data collection (ORCID, Semantic Scholar APIs)
- ⏳ Profile schema definition
- ⏳ AI profile generation
- ⏳ Matching engine implementation
- ⏳ Demo interface

---

## Technology Stack

### Core Technologies

| Category | Technology | Purpose |
|----------|------------|---------|
| Language | Python 3.x | Primary development language |
| Web Automation | Playwright MCP | JavaScript-rendered page scraping |
| AI/LLM | Anthropic Claude | Profile generation and matching |
| Data Storage | JSON files | Structured data storage |
| APIs | ORCID, Semantic Scholar, arXiv | Publication data collection |

### Python Dependencies (Issue #2)

```
anthropic              # Claude API client
requests               # HTTP requests
python-dotenv          # Environment variables
pandas                 # Excel/data manipulation
openpyxl              # Excel file handling
beautifulsoup4         # HTML parsing
lxml                  # XML/HTML parser
trafilatura           # Content extraction
streamlit (optional)   # Web demo interface
```

### MCP Server Configuration

Playwright MCP is configured for automated web navigation:

```bash
# Installation command used
claude mcp add npx @playwright/mcp@latest
```

**Status:** Installed but requires fresh Claude Code session to activate.

---

## Project Structure

```
grant-match/
├── data/                           # JSON data files
│   ├── department_inventory.json   # 8 departments mapped (Issue #3)
│   ├── faculty_from_fis.json       # 110 faculty from FIS (Issue #16)
│   ├── faculty_roster.json         # Enriched roster (Issue #4 - pending)
│   └── faculty_enriched.json       # With research data (Issue #5 - pending)
│
├── docs/                           # Documentation
│   ├── MCP_SETUP.md               # Playwright MCP configuration
│   ├── fis_data_analysis.md       # FIS data analysis report
│   └── web_scraping_findings.md   # Scraping investigation results
│
├── src/                            # Source code
│   └── data_collection/
│       ├── README.md              # Usage documentation
│       ├── scrape_faculty_listings.py      # Issue #4 script
│       └── scrape_faculty_websites.py      # Issue #5 script
│
├── FIS_All_Tenured_TT.xlsx        # Source Excel file (110 faculty)
├── scopus-vanderbilt.txt          # Scopus query template
├── README.md                      # Project overview
├── PROGRESS_SUMMARY.md            # Detailed progress tracking
├── DEMO_PLAN.md                   # Demo implementation plan
├── ISSUES_SUMMARY.md              # All 16 GitHub issues
├── brainstorming-notes.md         # Original planning notes
└── .gitignore                     # Git ignore rules
```

---

## Data Architecture

### Faculty Data Pipeline

```
FIS Data (Issue #16)
    ↓ data/faculty_from_fis.json
    • 110 faculty (80 Engineering + 30 CS)
    • 100% email coverage
    • Basic appointment info
    • NO websites, ORCID, or research info
    
    ↓
    
Faculty Listings Scraper (Issue #4)
    ↓ data/faculty_roster.json
    • Enriched with website URLs
    • Profile page links
    • Contact details verified
    
    ↓
    
Faculty Website Scraper (Issue #5)
    ↓ data/faculty_enriched.json
    • Research descriptions
    • Keywords and interests
    • Lab names and websites
    • CV/resume links
    
    ↓
    
Publication APIs (Issues #6-7)
    ↓ data/publications/{faculty_id}.json
    • ORCID publications
    • Semantic Scholar data
    • arXiv/bioRxiv preprints
    
    ↓
    
Profile Generation (Issues #8-10)
    ↓ data/profiles/{faculty_id}.json
    • AI-generated research summaries
    • Structured profile schema
```

### Data File Schemas

#### faculty_from_fis.json

```json
{
  "metadata": {
    "source_file": "FIS_All_Tenured_TT.xlsx",
    "extraction_date": "2025-11-04T...",
    "total_faculty": 110,
    "schools": ["School of Engineering", "College of Connected Computing"]
  },
  "faculty": [
    {
      "id": "faculty_020016",
      "person_id": 20016,
      "name": "Abkowitz, Mark",
      "first_name": "Mark",
      "last_name": "Abkowitz",
      "title": "Distinguished Professor of Civil & Environmental Engineering",
      "rank": "Distinguished Professor",
      "department": "Civil & Environmental Engineering",
      "department_code": "cee",
      "school": "School of Engineering",
      "email": "mark.abkowitz@vanderbilt.edu",
      "gender": "Male",
      "tenure_status": "Tenured",
      "is_active": true,
      "hire_date": "9/1/1987",
      "source_url": null,
      "website": null,
      "data_source": "FIS_All_Tenured_TT.xlsx"
    }
  ]
}
```

#### department_inventory.json

Contains 8 departments with URLs and metadata:
- `bme` - Biomedical Engineering (21 faculty)
- `chbe` - Chemical and Biomolecular Engineering (11 faculty)
- `cee` - Civil and Environmental Engineering (15 faculty)
- `cs` - Computer Science (30 faculty)
- `ece` - Electrical and Computer Engineering (17 faculty)
- `me` - Mechanical Engineering (16 faculty)
- `esm` - Engineering Science and Management
- `materials` - Materials Science Program

---

## Build and Run Commands

### Environment Setup (Issue #2)

```bash
# Install Python dependencies
pip install anthropic requests python-dotenv pandas openpyxl beautifulsoup4 lxml trafilatura

# Verify Playwright MCP installation
claude mcp list
```

### Running Data Collection Scripts

**Issue #4 - Faculty Listings Scraper:**

```bash
# Requires Playwright MCP active session
python3 src/data_collection/scrape_faculty_listings.py
```

**Issue #5 - Faculty Website Scraper:**

```bash
# Run after Issue #4 completes
python3 src/data_collection/scrape_faculty_websites.py
```

### Expected Outputs

| Script | Output File | Expected Content |
|--------|-------------|------------------|
| Issue #4 | `data/faculty_roster.json` | 110 faculty with website URLs |
| Issue #4 | `data/faculty_scraping_report.txt` | Statistics and coverage |
| Issue #5 | `data/faculty_enriched.json` | Profiles with research data |
| Issue #5 | `data/website_scraping_report.txt` | Extraction success metrics |

---

## Code Style Guidelines

### Python Style

- Use type hints for function signatures
- Follow PEP 8 naming conventions
- Use docstrings for all functions
- Include module-level docstrings explaining purpose

Example:
```python
def load_department_inventory() -> Dict:
    """Load the department inventory created in Issue #3."""
    with open('data/department_inventory.json', 'r') as f:
        return json.load(f)
```

### File Organization

- Scripts should be self-contained with clear entry points
- Use `if __name__ == '__main__':` for executable scripts
- Separate data loading, processing, and output generation
- Include progress logging for long-running operations

### Error Handling

- Gracefully handle missing files (provide fallbacks)
- Log errors with context (faculty name, URL)
- Continue processing on individual failures
- Save partial results for resume capability

### Rate Limiting

Always implement rate limiting for web requests:
```python
time.sleep(2)  # Between department pages (Issue #4)
time.sleep(3)  # Between faculty websites (Issue #5)
```

---

## Testing Strategy

### Manual Testing

- Verify JSON output structure matches expected schema
- Check data coverage statistics
- Review sample profiles for quality
- Validate API responses

### Quality Metrics

**Data Collection:**
- Website URL coverage: Target 95%+
- Research description coverage: Target 80%+
- Email coverage: 100% (already achieved)

**Profile Generation:**
- Average quality score: ≥4.0/5
- ≥80% rated Good or Excellent
- 0 hallucinated content
- Specific citations to real publications

---

## Security Considerations

### API Keys and Credentials

- Store in `.env` file (never commit to git)
- Use `python-dotenv` for loading
- Required variables:
  ```
  ANTHROPIC_API_KEY=sk-...
  SCOPUS_API_KEY=...
  ORCID_CLIENT_ID=...
  ORCID_CLIENT_SECRET=...
  ```

### Data Privacy

- FIS data contains PII (names, emails) - handle appropriately
- Publication data is public but cache responsibly
- Faculty profiles for internal use only

### Web Scraping Ethics

- Respect `robots.txt`
- Implement appropriate rate limiting
- Use identifiable User-Agent strings
- Scrape during off-peak hours when possible

---

## Common Tasks

### Adding a New Data Collection Script

1. Create script in `src/data_collection/`
2. Follow existing pattern: load → process → save → report
3. Add to Issue tracking documentation
4. Update PROGRESS_SUMMARY.md

### Modifying Data Schemas

1. Update schema documentation in relevant docs
2. Ensure backward compatibility or migration plan
3. Update dependent scripts
4. Regenerate affected data files

### Running with Playwright MCP

1. Start fresh Claude Code session in project directory
2. Verify MCP is active: `claude mcp list`
3. Modify script to use natural language MCP commands
4. Execute and monitor progress

---

## Troubleshooting

### Playwright MCP Not Working

```bash
# Verify installation
claude mcp list

# Reinstall if needed
claude mcp remove npx
claude mcp add npx @playwright/mcp@latest
```

### Missing Dependencies

```bash
# Install all required packages
pip install beautifulsoup4 lxml trafilatura pandas openpyxl
```

### Data File Not Found

Scripts expect data files in `data/` directory relative to project root:
- Always run scripts from project root
- Use relative paths: `data/filename.json`

---

## GitHub Issues Reference

### Phase 1: Setup & Infrastructure
- **#1** - Install and configure MCP server for web navigation ✓
- **#2** - Configure development environment and API access

### Phase 2: Research & Discovery
- **#3** - Map Vanderbilt Engineering department structure ✓
- **#16** - Extract and analyze FIS faculty data ✓

### Phase 3: Data Collection
- **#4** - Scrape faculty listings from department pages (infrastructure ✓)
- **#5** - Extract research information from faculty websites (infrastructure ✓)
- **#6** - Search preprint repositories for faculty publications
- **#7** - Retrieve publication data via ORCID and scholarly APIs

### Phase 4: Profile Generation
- **#8** - Define research profile data structure and schema
- **#9** - Design and test profile generation prompts
- **#10** - Build automated profile generation pipeline

### Phase 5: Validation & Refinement
- **#11** - Manual review and quality assessment of generated profiles
- **#12** - Improve profiles based on validation feedback

### Phase 6: Documentation & Demo
- **#13** - Create comprehensive profile dataset documentation
- **#14** - Create profile showcase interface
- **#15** - Create implementation roadmap and milestones

---

## Resources

### External Documentation
- [Playwright MCP Server](https://github.com/microsoft/playwright-mcp)
- [Playwright Documentation](https://playwright.dev/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Claude Code MCP Guide](https://docs.claude.com/en/docs/claude-code/mcp)

### Vanderbilt Resources
- Engineering Home: https://engineering.vanderbilt.edu/
- Engineering Faculty: https://engineering.vanderbilt.edu/people/
- URL Pattern: `https://engineering.vanderbilt.edu/people/{dept-code}/`

---

## Contact and Contribution

- **Repository:** https://github.com/vanderbilt-data-science/grant-match
- **Issues:** Track all work via GitHub issues
- **Documentation:** Maintain in `/docs` directory

---

**Last Updated:** 2025-11-04  
**Project Phase:** Data collection infrastructure complete, profile generation pending  
**Next Milestone:** Execute web scraping (Issues #4-5) or proceed to publication APIs (Issues #6-7)
