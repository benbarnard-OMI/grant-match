# Web Scraping Investigation - Findings

**Date:** 2025-11-04
**Issues:** #4, #5
**Status:** Playwright MCP Required (as expected)

---

## Investigation Summary

Attempted to scrape Vanderbilt Engineering faculty pages using multiple approaches to understand the data structure and accessibility.

## Approaches Tried

### 1. WordPress REST API

**Finding:** The site uses WordPress with a custom "person" post type

**Endpoint:** `https://engineering.vanderbilt.edu/wp-json/wp/v2/person`

**Result:** ❌ **Only 3 people available via API** (all staff, not faculty)
- Charity Backs (Senior Administrative Specialist, CEE)
- Hayley Britton (Digital Marketing Communications Specialist)
- Ryan Underwood (Director of Communications and Marketing)

**Conclusion:** Faculty data is NOT accessible via WordPress REST API

### 2. Direct HTML Fetching

**Attempt:** Used `curl` to fetch raw HTML from faculty listing pages

**Finding:** Page source contains:
- Title and meta tags
- Navigation structure
- Empty content containers
- JavaScript loading scripts

**Result:** ❌ **No faculty data in raw HTML**

The faculty listings are loaded dynamically via JavaScript after page render.

### 3. Data Attribute Search

**Attempt:** Searched for `data-*` attributes that might contain faculty information

**Result:** ❌ **No embedded data found**

### 4. JavaScript/API Call Analysis

**Attempt:** Looked for API endpoints or JavaScript files loading faculty data

**Finding:** Site uses various CDN scripts but no obvious faculty data API

**Result:** ❌ **No accessible data endpoint discovered**

---

## Confirmed Requirements

### JavaScript Rendering is Required

The faculty listing pages use **client-side JavaScript** to:
1. Fetch faculty data (likely from an internal endpoint or database)
2. Render the faculty grid/list dynamically
3. Handle filtering and pagination

### Playwright MCP is Necessary

To extract faculty data, we need:
- ✓ **Browser automation** (to execute JavaScript)
- ✓ **DOM access** (to extract rendered content)
- ✓ **Wait capabilities** (for asynchronous loading)

This is exactly what the Playwright MCP server (Issue #1) provides.

---

## Current Situation

### Playwright MCP Status

```bash
$ claude mcp list
npx: @playwright/mcp@latest  - ✗ Failed to connect
```

**Reason:** MCP server is installed but not currently connected/running in this session.

**Resolution:** Requires a fresh Claude Code session where the MCP can be activated.

---

## Data We Already Have

### FIS Data (Issue #16) ✅

**Excellent Coverage:**
- 110 faculty (80 Engineering + 30 Computer Science)
- 100% email addresses
- Complete names, departments, ranks
- Hire dates and tenure status

**Quality Score:** 95/100

**Missing from FIS:**
- Website URLs
- Research descriptions
- ORCID IDs
- Publication data

### What Web Scraping Would Add

**From Department Listings (Issue #4):**
- ✓ Personal/lab website URLs
- ✓ Profile page URLs
- ✓ Phone numbers
- ✓ Office locations
- ✓ Research interests (if listed)

**From Faculty Websites (Issue #5):**
- ✓ Research descriptions
- ✓ Keywords and interests
- ✓ Lab/group names
- ✓ CV/resume links
- ✓ Publication lists (if on site)
- ✓ Funding sources

---

## Recommended Path Forward

### Option A: Defer Web Scraping (Recommended)

**Rationale:**
1. FIS data provides excellent foundation (110 faculty, 100% emails)
2. Publication data can be obtained via APIs (Issues #6-7)
3. Many faculty websites link to Google Scholar, ORCID, etc. anyway
4. Website URLs can be manually added or searched for key faculty

**Next Steps:**
1. ✅ Use FIS data as primary faculty roster
2. ➡️ **Issue #6:** Search preprint repositories (arXiv, bioRxiv)
3. ➡️ **Issue #7:** Query ORCID and Semantic Scholar APIs for publications
4. ➡️ **Issues #8-10:** Design schema and generate profiles with publication data
5. ⏸️ Return to web scraping later if needed for validation

**Advantages:**
- Can make immediate progress on profile generation
- Publication data is more important than website descriptions
- Many APIs provide research area keywords automatically
- Profiles can be generated with publication-based summaries

### Option B: Execute Web Scraping with Playwright MCP

**Requirements:**
1. Start fresh Claude Code session in this directory
2. Playwright MCP will auto-activate (installed in Issue #1)
3. Run scraping scripts with MCP integration
4. Extract all data as planned

**Timeline:**
- Setup: 5 minutes (new session)
- Scraping execution: ~30-45 minutes total
  - Issue #4: 15-20 minutes (department listings)
  - Issue #5: 15-30 minutes (faculty websites)

**Advantages:**
- Completes data collection as originally planned
- Provides website URLs for direct linking
- Gets research descriptions in faculty's own words
- May find information not in publications

---

## Recommendation

**Proceed with Option A** (defer web scraping) because:

1. **Data We Have is Excellent**
   - 110 faculty with complete contact info
   - Ready for publication queries immediately
   - 100% email coverage for future validation

2. **APIs Provide Key Information**
   - ORCID: Publications, research areas, grants
   - Semantic Scholar: Research topics, citations
   - arXiv/bioRxiv: Recent work, abstracts
   - CrossRef: Publication metadata

3. **Profile Generation Can Proceed**
   - Publications provide research focus
   - Abstracts describe methodology
   - Co-authors show collaborations
   - Grants indicate funding areas

4. **Time Efficiency**
   - Can start profile generation immediately
   - Web scraping can be added later if needed
   - For proof-of-concept, publication data is sufficient

5. **Demo Readiness**
   - Publication-based profiles are highly credible
   - Easy to explain data sources (ORCID, Semantic Scholar)
   - Can demonstrate matching without website dependency

---

## If Web Scraping is Required

### Execution Plan

**Session Setup:**
```bash
# 1. Start new Claude Code session
cd /Users/spencejb/Documents/projects/grant-match

# 2. Verify Playwright MCP is active
claude mcp list
# Should show: ✓ @playwright/mcp@latest

# 3. Run faculty listing scraper
python3 src/data_collection/scrape_faculty_listings.py
# Output: data/faculty_roster.json

# 4. Run website content scraper
python3 src/data_collection/scrape_faculty_websites.py
# Output: data/faculty_enriched.json
```

**Expected Results:**
- ~95%+ website URL coverage
- ~80-90% research description extraction
- ~6070% CV/resume link discovery
- Complete faculty roster ready for profile generation

---

## Technical Notes

### Why REST APIs Failed

Most WordPress sites expose their content via REST API, but:
- Faculty data is likely in a **custom database table** (not WordPress posts)
- Or uses a **JavaScript framework** that fetches from a separate backend
- Or implements **access control** limiting API access
- Or uses a **third-party faculty directory system**

### Why Playwright MCP is the Solution

Playwright MCP can:
- ✓ Execute JavaScript to trigger data loading
- ✓ Wait for asynchronous content to appear
- ✓ Extract from the rendered DOM
- ✓ Handle pagination and filtering
- ✓ Navigate to individual faculty pages
- ✓ Parse various website structures

---

## Conclusion

**Current Recommendation:** **Proceed to Issues #6-7** (publication APIs)

The FIS data we have is excellent and sufficient for initial profile generation. Publication data from APIs will provide:
- Research descriptions (from abstracts)
- Keywords and topics (from classifications)
- Methodologies (from paper content)
- Collaboration networks (from co-authors)
- Impact metrics (citations)

Web scraping can be completed later if:
- Validation shows gaps in data
- Website descriptions add significant value
- Direct faculty website links are needed
- Profile quality needs improvement

**Web scraping is available and ready** - just requires activating Playwright MCP in a new session.

---

**Document Status:** Investigation complete, recommendation provided
**Last Updated:** 2025-11-04
**Next Step:** Proceed to Issue #6 (preprint repositories) or activate Playwright MCP for Issues #4-5
