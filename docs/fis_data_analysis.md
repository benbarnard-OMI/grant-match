# FIS Data Analysis Report

**Date:** 2025-11-04
**Issue:** #16 - Extract and analyze FIS faculty data
**Source File:** FIS_All_Tenured_TT.xlsx

---

## Executive Summary

Successfully extracted and analyzed faculty data from the Vanderbilt FIS (Faculty Information System) database. Identified **110 active tenured/tenure-track faculty** across 6 engineering departments (including Computer Science).

## Data Source Analysis

### File Structure

**File:** `FIS_All_Tenured_TT.xlsx`
- **Total records:** 1,312 faculty across all Vanderbilt schools
- **Columns:** 18 fields including personal info, appointment details, and contact information

### Available Fields

1. **Identification:** Person #, Person Id, Full Name, Last Name, First Name, Middle Name
2. **Demographics:** Gender
3. **Appointment:** School, Unit, Rank, Full Title, Appt Type, Tenure, Hire Date
4. **Status:** Is Active?, Entity
5. **Contact:** E-mail Address (VU), E-mail Address (VUMC)

### Notable Absences

- **No ORCID IDs:** Will need to obtain from other sources
- **No research areas:** Will need web scraping
- **No publication lists:** Will need API queries
- **No personal websites:** Will need web scraping

## Engineering Faculty Breakdown

### Schools Included

1. **School of Engineering:** 80 faculty
2. **College of Connected Computing:** 30 faculty (Computer Science)

**Combined Total:** 110 faculty

### By Department

| Department | Code | Count | Percentage |
|------------|------|-------|------------|
| Computer Science | cs | 30 | 27.3% |
| Biomedical Engineering | bme | 21 | 19.1% |
| Electrical and Computer Engineering | ece | 17 | 15.5% |
| Mechanical Engineering | me | 16 | 14.5% |
| Civil & Environmental Engineering | cee | 15 | 13.6% |
| Chemical & Biomolecular Engineering | chbe | 11 | 10.0% |
| **Total** | | **110** | **100%** |

### By Academic Rank

| Rank | Count | Percentage |
|------|-------|------------|
| Professor | 56 | 50.9% |
| Assistant Professor | 27 | 24.5% |
| Associate Professor | 20 | 18.2% |
| Distinguished Professor | 4 | 3.6% |
| University Distinguished Professor | 3 | 2.7% |
| **Total** | **110** | **100%** |

### Faculty Distribution

- **Senior Faculty (Professor):** 56 (50.9%)
- **Mid-Career (Associate Professor):** 20 (18.2%)
- **Junior Faculty (Assistant Professor):** 27 (24.5%)
- **Distinguished:** 7 (6.4%)

## Data Quality Assessment

### Completeness Score: 95/100

| Field | Coverage | Notes |
|-------|----------|-------|
| Name (Full, First, Last) | 100% | Complete |
| Email (VU) | 100% | All 110 faculty have email |
| Department/Unit | 100% | Complete |
| Rank/Title | 100% | Complete |
| Active Status | 100% | All marked "Yes" (filtered) |
| Gender | ~95% | Few missing values |
| Hire Date | ~98% | Mostly complete |
| Tenure Status | ~95% | Mostly complete |
| ORCID | 0% | **Not in dataset** |
| Research Areas | 0% | **Not in dataset** |
| Website | 0% | **Not in dataset** |

### Data Quality Notes

**Strengths:**
- ✓ 100% email coverage
- ✓ Consistent naming conventions
- ✓ Clean department categorization
- ✓ All faculty marked as active
- ✓ Standardized rank terminology

**Limitations:**
- ✗ No ORCID identifiers
- ✗ No research area information
- ✗ No personal/lab website URLs
- ✗ No publication data
- ✗ Computer Science under different school (required manual merging)

## Department Name Standardization

### Web vs. FIS Naming Differences

| FIS Unit Name | Web Department Name | Code |
|---------------|---------------------|------|
| Civil & Environmental Engineering | Civil and Environmental Engineering | cee |
| Chemical & Biomolecular Engineering | Chemical and Biomolecular Engineering | chbe |
| (All others match) | | |

**Action Taken:** Created standardized department codes for consistent identification.

## Output Files Created

### 1. `data/faculty_from_fis.json`

**Structure:**
```json
{
  "metadata": {
    "source_file": "FIS_All_Tenured_TT.xlsx",
    "extraction_date": "2025-11-04T...",
    "total_faculty": 110,
    "schools": ["School of Engineering", "College of Connected Computing"],
    "filter_criteria": "Active tenured/tenure-track faculty"
  },
  "faculty": [
    {
      "id": "faculty_XXXXXX",
      "person_id": 12345,
      "name": "Full Name",
      "first_name": "First",
      "last_name": "Last",
      "middle_name": "Middle",
      "title": "Full Title",
      "rank": "Professor",
      "department": "Department Name",
      "department_code": "dept",
      "school": "School Name",
      "email": "email@vanderbilt.edu",
      "gender": "M/F",
      "tenure_status": "Tenured/Tenure Track",
      "is_active": true,
      "hire_date": "MM/DD/YYYY",
      "source_url": null,
      "website": null,
      "data_source": "FIS_All_Tenured_TT.xlsx"
    }
  ],
  "department_summary": {
    "bme": 21,
    "ece": 17,
    ...
  }
}
```

**Purpose:** Serves as base faculty roster for enrichment via web scraping and API calls.

## Missing Data - Next Steps

### To Be Obtained via Web Scraping (Issues #4-5)

1. **Personal/Lab Website URLs**
   - Source: Department faculty pages
   - Method: Playwright MCP navigation

2. **Research Descriptions**
   - Source: Individual faculty websites
   - Method: Content extraction from personal pages

3. **Current Research Areas**
   - Source: Faculty profile pages, lab websites
   - Method: Text analysis and keyword extraction

### To Be Obtained via API Queries (Issue #7)

1. **ORCID IDs**
   - Attempt name-based ORCID searches
   - Validate via affiliation matching

2. **Publication Lists**
   - ORCID API (if IDs available)
   - Semantic Scholar API (name + affiliation)
   - OpenAlex API (alternative)

3. **Publication Metadata**
   - Titles, abstracts, years, citations
   - DOIs and PMIDs where available

## Integration with Department Inventory

### Cross-Reference Results

Compared FIS data with web-scraped department inventory (Issue #3):

**Matches:**
- All 6 FIS departments have corresponding web pages
- URL pattern confirmed: `https://engineering.vanderbilt.edu/people/{dept-code}/`

**Discrepancies:**
- **Engineering Science and Management (esm):** Not in FIS data (may be administrative)
- **Materials Science:** Interdisciplinary program, not a department (faculty have primary departments)

**Conclusion:** FIS data aligns well with web structure for the 6 main departments.

## Recommendations

### For Profile Generation (Issues #8-10)

1. **Use FIS data as bootstrap:**
   - Names, departments, emails are reliable
   - Provides faculty counts for validation

2. **Enrich via web scraping:**
   - Personal websites (Issue #5)
   - Research descriptions
   - Lab affiliations

3. **Validate via API data:**
   - Cross-check publications with ORCID/Semantic Scholar
   - Use publications to verify research areas

### For Data Quality

1. **Prioritize by rank:**
   - Start profile generation with Full Professors (56)
   - They typically have more publications and clearer research profiles

2. **Department-specific strategies:**
   - CS: 30 faculty, largest department
   - BME: 21 faculty, may have more interdisciplinary work
   - Smaller depts (CHBE: 11): Complete coverage more achievable

3. **Email availability:**
   - 100% coverage enables direct validation with faculty later
   - Can send profile review requests

## Statistics Summary

### Coverage by Department

```
Computer Science:              30 faculty (27%)
Biomedical Engineering:        21 faculty (19%)
Electrical & Computer Eng:     17 faculty (15%)
Mechanical Engineering:        16 faculty (15%)
Civil & Environmental Eng:     15 faculty (14%)
Chemical & Biomolecular Eng:   11 faculty (10%)
```

### Seniority Distribution

```
Full Professors:           56 (51%)
Assistant Professors:      27 (25%)
Associate Professors:      20 (18%)
Distinguished Titles:       7 ( 6%)
```

### Data Completeness

```
Core Identity Data:        100%
Contact Information:       100%
Appointment Details:        98%
Research Information:        0% (requires scraping/APIs)
ORCID Coverage:             0% (requires lookup)
```

## Technical Implementation

### Code Used

Python with pandas and openpyxl:
- Filtered for School == "School of Engineering" OR "College of Connected Computing"
- Extracted 18 fields per faculty member
- Created standardized department codes
- Generated JSON output with metadata

### Data Transformation

1. Person ID → faculty_XXXXXX (6-digit padded ID)
2. Unit → department_code mapping
3. Active status filtering (only "Yes")
4. Email normalization (VU addresses only)

## Conclusion

**Issue #16 Complete:**
- ✓ FIS data successfully analyzed
- ✓ 110 Engineering faculty identified and extracted
- ✓ Data quality assessed (95/100)
- ✓ Structured JSON output created
- ✓ Integration with department inventory confirmed
- ✓ Missing data types identified
- ✓ Next steps documented

**Key Findings:**
1. Solid base data available for 110 faculty
2. 100% email coverage enables validation
3. No ORCID data - will require API lookups
4. Research information requires web scraping
5. Computer Science separated into different school

**Ready for Next Steps:**
- Issues #4-5: Web scraping for enrichment
- Issue #7: Publication data via APIs
- Issues #8-10: Profile generation

---

**Document Status:** Complete
**Last Updated:** 2025-11-04
**Issue Status:** #16 - Complete ✓
