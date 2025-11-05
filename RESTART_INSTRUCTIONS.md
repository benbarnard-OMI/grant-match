# Restart Instructions for Web Scraping

**Session:** Restarting to activate Playwright MCP
**Goal:** Complete Issues #4 and #5 (web scraping)

---

## What to Do

### 1. Restart Claude Code

Exit this session and restart in this directory:

```bash
cd /Users/spencejb/Documents/projects/grant-match
claude
```

### 2. Verify Playwright MCP is Active

```bash
claude mcp list
```

**Expected output:**
```
npx: @playwright/mcp@latest  - ✓ Connected
```

If it shows "Failed to connect", try:
```bash
claude mcp add npx @playwright/mcp@latest
```

---

## What's Ready to Run

### Issue #4: Faculty Listings Scraper

**Script:** `src/data_collection/scrape_faculty_listings.py`

**Current approach (needs modification for Playwright MCP):**
The script is structured but needs Playwright MCP integration. When you restart:

**Tell Claude:**
```
"I need to scrape faculty listings from Vanderbilt Engineering department pages.
Use Playwright MCP to navigate to each URL in data/department_inventory.json,
extract faculty information (names, titles, emails, websites), match with FIS data,
and save to data/faculty_roster.json"
```

**Departments to scrape (7 total):**
1. Biomedical Engineering (21 expected)
2. Chemical and Biomolecular Engineering (11 expected)
3. Civil and Environmental Engineering (15 expected)
4. Computer Science (30 expected)
5. Electrical and Computer Engineering (17 expected)
6. Mechanical Engineering (16 expected)
7. Engineering Science and Management (unknown)

**Expected output:**
- `data/faculty_roster.json` - ~110 faculty with website URLs
- `data/faculty_scraping_report.txt` - Statistics

**Estimated time:** 15-20 minutes

---

### Issue #5: Faculty Websites Scraper

**Script:** `src/data_collection/scrape_faculty_websites.py`

**After Issue #4 completes:**

**Tell Claude:**
```
"Now scrape research information from each faculty's personal website.
Use Playwright MCP to navigate to the website URLs in data/faculty_roster.json,
extract research descriptions, keywords, CV links, lab names, and publications,
then save to data/faculty_enriched.json"
```

**Expected output:**
- `data/faculty_enriched.json` - Full research data for all faculty
- `data/website_scraping_report.txt` - Statistics

**Estimated time:** 15-30 minutes (110 websites × 3 sec delay)

---

## Alternative: Direct Playwright MCP Commands

If the Python scripts don't work perfectly with Playwright MCP, you can use direct commands:

### For Issue #4 (Faculty Listings):

```
"Navigate to https://engineering.vanderbilt.edu/people/biomedical-engineering/
using Playwright. Wait for the faculty grid to load. Extract all visible faculty
with their:
- Name
- Title
- Email
- Phone
- Website URL
- Profile link

Return as JSON array."
```

Then repeat for each department and manually merge with FIS data.

### For Issue #5 (Faculty Websites):

```
"Navigate to [faculty website URL] using Playwright. Extract:
- Main research description text
- Research keywords/interests
- Lab or group name
- CV/resume PDF links
- Publications listed
- Courses taught
- Funding sources mentioned

Return as structured JSON."
```

Then repeat for each faculty member.

---

## What We Have Already

### Completed (This Session):

✅ **Issue #1:** Playwright MCP installed and configured
✅ **Issue #3:** Department structure mapped (8 departments)
✅ **Issue #16:** FIS data analyzed (110 faculty)
✅ **Issues #4-5:** Scripts created and documented

### Data Files Ready:

- `data/department_inventory.json` - 7 URLs to scrape
- `data/faculty_from_fis.json` - 110 faculty to enrich
- `data/wordpress_people_raw.json` - Confirmed no faculty in API

### Scripts Ready:

- `src/data_collection/scrape_faculty_listings.py`
- `src/data_collection/scrape_faculty_websites.py`
- `src/data_collection/README.md` - Complete documentation

---

## Expected Results After Scraping

### data/faculty_roster.json

```json
{
  "metadata": {
    "total_faculty": 110,
    "data_sources": ["FIS", "web_scraping"]
  },
  "faculty": [
    {
      "id": "faculty_123456",
      "name": "Dr. Jane Smith",
      "department_code": "bme",
      "email": "jane.smith@vanderbilt.edu",
      "website": "https://engineering.vanderbilt.edu/~jsmith/",
      "phone": "615-xxx-xxxx",
      "office": "FGH 123",
      "profile_url": "https://...",
      ...
    }
  ]
}
```

**Expected coverage:**
- Website URLs: 95-98%
- Phone numbers: 90-95%
- Office locations: 85-90%

### data/faculty_enriched.json

```json
{
  "faculty": [
    {
      "id": "faculty_123456",
      "name": "Dr. Jane Smith",
      ...
      "website_data": {
        "research_description": "My research focuses on neural interfaces...",
        "research_keywords": ["neural interfaces", "BCI", "neuroprosthetics"],
        "lab_name": "Neural Engineering Lab",
        "cv_url": "https://.../cv.pdf",
        "publications_listed": 12,
        "extraction_success": true
      }
    }
  ]
}
```

**Expected coverage:**
- Research descriptions: 80-90%
- Keywords: 85-95%
- CV links: 60-75%
- Lab names: 50-70%

---

## Success Criteria

After completing web scraping, you should have:

✅ 110 faculty with complete data from 3 sources (FIS + web listings + websites)
✅ 95%+ with personal website URLs
✅ 80%+ with research descriptions
✅ Ready for profile generation (Issues #8-10)

---

## If Issues Arise

### Playwright MCP Not Connecting

```bash
# Check if installed
claude mcp list

# Reinstall if needed
claude mcp remove npx
claude mcp add npx @playwright/mcp@latest

# Check Node.js version (needs 18+)
node --version
```

### Pages Not Loading

- Increase wait times in Playwright commands
- Check network connectivity
- Try one department page manually first

### Data Not Extracting

- Check if page structure has changed
- Look at raw HTML to confirm content exists
- May need to adjust selectors/parsing logic

---

## After Web Scraping Completes

Next steps will be:

1. **Issue #8:** Define research profile schema
2. **Issue #9:** Design AI profile generation prompts
3. **Issue #10:** Generate profiles using enriched data
4. **Issues #11-12:** Validation and refinement

With website data, you'll have rich research descriptions to feed into the AI profile generation!

---

## Quick Start Commands (After Restart)

```bash
# 1. Verify MCP
claude mcp list

# 2. Start with Issue #4
# Tell Claude: "Run the faculty listing scraper using Playwright MCP"

# 3. Then Issue #5
# Tell Claude: "Now run the website scraper using Playwright MCP"

# 4. Check results
ls -lh data/faculty_roster.json
ls -lh data/faculty_enriched.json
```

---

**Status:** Ready to restart and execute web scraping
**Last Updated:** 2025-11-04
**Next Action:** Restart Claude Code in this directory
