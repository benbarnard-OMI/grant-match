# Grant Match Demo - Implementation Plan

**Status:** Planning Phase - No Code Written Yet
**Target:** Research office leadership demonstration
**Goal:** Prove value of AI-powered grant matching with live demo

---

## Demo Objectives

### What We're Proving
1. **Profile Generation Quality:** AI can create accurate, useful faculty research summaries
2. **Matching Capability:** System can identify relevant matches with specific rationales
3. **Real-time Performance:** Matching can happen quickly enough for live demo
4. **Practical Value:** Results are actionable and better than manual process

### What We're NOT Building (Yet)
- Full production system
- Email notification infrastructure
- Feedback collection mechanisms
- Automated profile update pipelines
- Multi-user interface

---

## Demo Architecture

### Component Overview

```
┌─────────────────────┐
│   Data Sources      │
│  - ORCID API        │
│  - Scopus           │
│  - NIH Reporter     │
│  - NSF Awards       │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Profile Generator   │
│  - Fetch pubs       │
│  - Summarize with   │
│    AI reasoning     │
│  - Cache profiles   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Profile Database   │
│   (Local JSON)      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Matching Engine    │
│  - Load RFP         │
│  - Score all profs  │
│  - Generate reasons │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Demo Interface    │
│  - Show profiles    │
│  - Input RFP        │
│  - Display matches  │
└─────────────────────┘
```

---

## Phase 1: Data Collection (Before Demo)

### Faculty List
**Source:** Vanderbilt Engineering website or FIS_All_Tenured_TT.xlsx

**Target:** 50-100 Engineering faculty (manageable for demo)

**Data to Collect:**
- Name
- Department
- Title/Position
- ORCID ID (if available)
- Email (for context)
- Personal website/research page

**Implementation Approach:**
```
Option A: Manual extraction from FIS Excel file
  - Filter for School of Engineering
  - Extract ORCID IDs if present
  - Supplement with web scraping if needed

Option B: Department website scraping
  - Iterate through department faculty pages
  - Extract structured data
  - Cross-reference with FIS data
```

### Publication Data
**Primary Source:** ORCID API (if IDs available)

**Backup Source:** Scopus API (using scopus-vanderbilt.txt query as template)

**Data Structure:**
```json
{
  "faculty_id": "unique_id",
  "name": "Dr. Jane Smith",
  "orcid": "0000-0002-1234-5678",
  "publications": [
    {
      "title": "Novel Neural Interface Design",
      "year": 2024,
      "doi": "10.1234/example",
      "pmid": "12345678",
      "abstract": "Full abstract text...",
      "journal": "Nature Neuroscience",
      "citations": 15
    }
  ]
}
```

**Implementation Steps:**
1. For each faculty with ORCID: Query ORCID API for works
2. For each work: Fetch full metadata (DOI, abstract, citations)
3. Filter: Last 5 years of publications (2020-2025)
4. Prioritize: Recent papers, high citations, review articles
5. Store: Cache all data locally to avoid re-fetching

### Grant Data (Optional Enhancement)
**Sources:**
- NIH Reporter API (for NIH grants)
- NSF Awards API (for NSF grants)

**Why Optional:**
- Publications may be sufficient for demo
- Grants add credibility but increase complexity
- Include if time permits

---

## Phase 2: Profile Generation

### AI Profile Generation Strategy

**Input for Each Faculty:**
- Name and affiliation
- List of recent publications (titles, abstracts, years)
- Any grants (if available)
- Research statement from website (if available)

**Prompt Structure:**
```
You are creating a research profile for grant matching purposes.

Faculty: Dr. [Name], [Department], [University]

Publications (last 5 years):
[Publication list with titles and abstracts]

Task: Generate a concise research profile (200-300 words) that:
1. Identifies primary research areas and methods
2. Highlights key contributions and innovations
3. Notes interdisciplinary connections
4. Mentions technical capabilities and expertise
5. Is specific enough for grant matching

Output format:
{
  "research_areas": ["area1", "area2", "area3"],
  "summary": "narrative summary text",
  "keywords": ["kw1", "kw2", "kw3"],
  "methodologies": ["method1", "method2"],
  "recent_focus": "current research direction"
}
```

**Processing Approach:**
- Batch processing: 10-20 faculty at a time
- Use high-quality reasoning model (e.g., Claude Sonnet)
- Cache results to avoid regeneration
- Manual review of sample profiles for quality check

**Quality Criteria:**
- Accurate representation of research
- Specific (not generic)
- Actionable for matching
- Readable by faculty member

---

## Phase 3: Demo Interface

### Technology Options

**Option A: Python Script + Terminal Output**
- Simplest implementation
- Quick to build
- Easy to debug
- Less visually impressive

**Option B: Streamlit Web App**
- Interactive UI
- Professional appearance
- Easy to share/deploy
- Minimal front-end code

**Option C: Jupyter Notebook**
- Good for exploration
- Can show code + results
- Interactive
- Less polished than web app

**Recommendation:** Start with Option A (script), upgrade to Option B (Streamlit) if time permits.

### Interface Requirements

**Pre-Demo Setup View:**
```
=== Grant Match Demo Setup ===

Loaded Profiles: 75 faculty
Last Updated: 2025-11-04

Sample Profiles:
1. Dr. Jane Smith (Biomedical Engineering)
   - Neural interfaces, brain-computer systems
   - 12 publications (2020-2024)

2. Dr. John Doe (Electrical Engineering)
   - Signal processing, machine learning
   - 18 publications (2020-2024)

[View Full Profile] [Regenerate Profile] [Continue to Demo]
```

**Live Demo View:**
```
=== Grant Match Demo ===

Input RFP:
[ Paste RFP text or upload PDF ]
[Analyze Now]

Results: Top 15 Matches

1. Dr. Jane Smith (Score: 94/100)
   Department: Biomedical Engineering

   RATIONALE:
   Dr. Smith's 2024 paper on adaptive neural interfaces
   (PMID: 38123456) directly addresses this RFP's focus
   on novel brain-computer paradigms (Section 2.3). Her
   methodology using multi-modal sensing aligns with the
   RFP's technical requirements for real-time signal
   processing.

   KEY ALIGNMENTS:
   - Neural interface design → RFP Section 2.3
   - Real-time processing → RFP Section 3.1
   - Clinical validation experience → RFP Section 4.2

   SUGGESTED APPROACH:
   Extend her current adaptive algorithm work to address
   the RFP's multi-user scenario requirements.

[View Full Profile] [Next Match]
```

---

## Phase 4: Matching Engine

### Matching Algorithm

**Single-Stage Reasoning Approach:**

```
For each faculty profile:
  Input to AI:
    - RFP full text
    - Faculty research profile
    - Faculty publications (recent)

  Output from AI:
    - Relevance score (0-100)
    - Specific rationale (2-3 sentences)
    - Key alignment points (3-5 bullet points)
    - Suggested approach (1-2 sentences)
```

**Prompt Template:**
```
You are an expert grant matching system.

RFP DETAILS:
[Full RFP text or summary]

FACULTY PROFILE:
Name: [Name]
Department: [Department]
Research Summary: [AI-generated summary]
Recent Publications:
[Top 5 recent publications with titles and abstracts]

TASK:
Evaluate how well this faculty member's research aligns
with the RFP requirements.

OUTPUT (JSON):
{
  "score": 0-100,
  "rationale": "2-3 specific sentences citing actual publications and RFP sections",
  "alignments": [
    "Faculty expertise → RFP requirement",
    ...
  ],
  "suggested_approach": "How faculty could approach this opportunity"
}

REQUIREMENTS FOR RATIONALE:
- Cite specific publications by title or PMID
- Reference specific RFP sections
- Explain WHY there's a match
- Be concrete, not generic
```

**Processing Strategy:**
- Parallel processing where possible (API rate limits permitting)
- Progress bar for live demo (shows it's working)
- Fallback to cached results if API fails
- Sort by score descending
- Display top 10-15 matches

---

## Phase 5: Test RFP Selection

### RFP Requirements for Demo

**Criteria:**
1. **Relevant to Engineering:** Matches faculty expertise areas
2. **Diverse Topics:** Show breadth of matching capability
3. **Recent:** Current or recent deadlines (looks realistic)
4. **Varied Agencies:** NSF, NIH, DOE, DARPA, etc.
5. **Different Scales:** Some targeted, some broad

### Suggested Test RFPs

**Option 1: Pre-selected RFPs (Safe)**
- Select 3-4 RFPs before demo
- Pre-run matching to verify quality
- Have backup results ready
- Ask audience to pick which one to demo

**Option 2: Audience-suggested RFPs (Bold)**
- Ask audience for RFP suggestions
- Run matching live on their choice
- Higher risk but more impressive
- Need fast API responses

**Recommendation:** Hybrid approach
- Have 2-3 pre-selected as backup
- Offer to run on audience suggestion if they have one
- Shows confidence while managing risk

### Where to Find Test RFPs

**Sources:**
1. **NSF Solicitations:** https://www.nsf.gov/funding/
   - Engineering directorate programs
   - CAREER awards
   - CISE programs

2. **NIH Funding:** https://grants.nih.gov/funding/
   - NIBIB for biomedical engineering
   - R01, R21 mechanisms

3. **DOE Funding:** https://science.osti.gov/grants
   - Energy research programs

4. **DARPA:** https://www.darpa.mil/work-with-us/opportunities
   - Defense research programs

---

## Implementation Timeline

### Minimum Viable Demo (3-4 days)

**Day 1: Data Collection**
- Extract 50 Engineering faculty from FIS data
- Collect ORCID IDs or publication lists
- Structure data files
- Test ORCID/Scopus API access

**Day 2: Profile Generation**
- Write profile generation prompt
- Process 50 faculty through AI
- Review and refine 5-10 profiles manually
- Cache all results

**Day 3: Matching Engine**
- Select 2-3 test RFPs
- Write matching prompt
- Run test matches
- Verify rationale quality
- Build basic demo script

**Day 4: Demo Polish**
- Create presentation flow
- Test end-to-end
- Prepare backup slides/results
- Practice demo delivery

### Enhanced Demo (1-2 weeks)

Add if time permits:
- Web interface (Streamlit)
- More faculty (100+)
- Grant data integration
- Better visualizations
- Comparison with manual matching

---

## Technical Implementation Details

### File Structure
```
grant-match/
├── data/
│   ├── faculty_list.json          # Faculty roster
│   ├── publications/               # Cached publication data
│   │   ├── faculty_001.json
│   │   └── ...
│   └── profiles/                   # Generated profiles
│       ├── faculty_001.json
│       └── ...
├── rfps/
│   ├── test_rfp_nsf_001.txt
│   ├── test_rfp_nih_002.txt
│   └── ...
├── src/
│   ├── data_collection/
│   │   ├── fetch_orcid.py         # ORCID API integration
│   │   ├── fetch_scopus.py        # Scopus API integration
│   │   └── parse_fis.py           # Parse Excel data
│   ├── profile_generation/
│   │   ├── generate_profiles.py   # AI profile generation
│   │   └── prompts.py             # Prompt templates
│   ├── matching/
│   │   ├── match_engine.py        # Core matching logic
│   │   └── prompts.py             # Matching prompts
│   └── demo/
│       ├── cli_demo.py            # Terminal demo
│       └── streamlit_app.py       # Web demo (optional)
├── tests/
│   └── test_matching.py           # Validation tests
├── requirements.txt               # Python dependencies
└── README.md
```

### Key Dependencies

**Python Packages:**
```
# Core
anthropic              # Claude API
requests               # HTTP requests
python-dotenv          # Environment variables

# Data Processing
pandas                 # Excel/data manipulation
openpyxl              # Excel file handling

# Optional (for web demo)
streamlit             # Web interface
plotly                # Visualizations

# APIs
orcid                 # ORCID API client
pybliometrics         # Scopus API client
```

### Environment Variables
```
ANTHROPIC_API_KEY=sk-...
SCOPUS_API_KEY=...
ORCID_CLIENT_ID=...
ORCID_CLIENT_SECRET=...
```

---

## Risk Mitigation

### Technical Risks

**Risk:** API failures during live demo
**Mitigation:**
- Cache all profile generation beforehand
- Pre-run matching on test RFPs
- Have backup results ready
- Can show cached results if live fails

**Risk:** Poor match quality
**Mitigation:**
- Test thoroughly before demo
- Refine prompts based on test results
- Have 2-3 different RFPs to choose from
- Frame as prototype needing iteration

**Risk:** Slow API response times
**Mitigation:**
- Batch requests where possible
- Show progress bar during processing
- Set expectations ("this takes 30-60 seconds")
- Consider parallel processing

### Content Risks

**Risk:** Inaccurate faculty profiles
**Mitigation:**
- Manual review of sample profiles
- Transparency about data sources
- Frame as "automated first draft"
- Show how faculty can correct

**Risk:** Missing obvious matches
**Mitigation:**
- Process ALL faculty (no filtering)
- Show top 15-20, not just top 5
- Explain scoring methodology
- Acknowledge it's a discovery tool, not replacement for human judgment

**Risk:** Overconfident bad matches
**Mitigation:**
- Show rationale for inspection
- Explain feedback loop concept
- Acknowledge false positives expected
- Emphasize learning system

---

## Success Metrics for Demo

### Minimum Success
- System runs without crashing
- Generates plausible matches
- Rationales are specific (cite publications)
- Audience understands the concept

### Good Success
- Matches are clearly relevant
- Audience recognizes faculty expertise correctly
- Rationales are impressive/insightful
- Questions indicate interest

### Excellent Success
- Audience identifies non-obvious matches they wouldn't have found
- Faculty expertise descriptions are accurate
- Stakeholders want to pilot immediately
- Specific use cases discussed

---

## Demo Script Outline

### Introduction (2 min)
"Research universities face a challenge: thousands of faculty, hundreds of RFPs per year, manual matching process. We've built an AI system to automate this with intelligent, contextualized recommendations."

### Show Profiles (5 min)
- Display 3-4 example faculty profiles
- Explain data sources (ORCID, publications)
- Ask: "Does this accurately represent their research?"
- Discuss: Automated generation + annual validation

### Live Matching (10 min)
- Load RFP (pre-selected or audience choice)
- Run matching engine (show progress)
- Display top 10-15 matches with rationales
- Highlight: Specific citations, RFP section references
- Discuss: Why these matches vs. others

### Discussion (10 min)
- Feedback on match quality
- Questions about implementation
- Data availability discussion
- Pilot planning

---

## Post-Demo Next Steps

### If Interest is High
1. Identify pilot department/school
2. Request access to:
   - Complete faculty ORCID list
   - Recent RFPs and application data
   - Institutional publication database
3. Propose pilot timeline (3 months)
4. Define success metrics
5. Discuss budget/resources

### If Interest is Moderate
1. Refine based on feedback
2. Propose smaller proof-of-concept
3. Offer to process specific RFP
4. Schedule follow-up in 1 month

### If Interest is Low
1. Document feedback
2. Identify specific objections
3. Determine if solvable
4. Pivot or iterate

---

## Open Technical Questions

### To Resolve Before Implementation

1. **ORCID Coverage:** What percentage of Engineering faculty have ORCID IDs in FIS data?

2. **API Access:** Do we have institutional Scopus API access? NIH Reporter API key?

3. **Computing Resources:** Will matching 50-100 faculty in real-time be fast enough for live demo?

4. **RFP Format:** Text files? PDFs? URLs? Need to handle parsing?

5. **Profile Length:** 200 words? 500 words? Trade-off between detail and token cost.

6. **Match Threshold:** What score (0-100) is worth notifying? 70? 80? 90?

---

## Next Actions

### Immediate (Before Starting Implementation)

1. **Validate FIS Data:**
   - Open FIS_All_Tenured_TT.xlsx
   - Count Engineering faculty
   - Check for ORCID IDs
   - Assess data completeness

2. **Test API Access:**
   - Verify ORCID API credentials
   - Test Scopus query from scopus-vanderbilt.txt
   - Confirm Claude API access

3. **Select Faculty Sample:**
   - Choose 50 diverse Engineering faculty
   - Prioritize those with clear research areas
   - Ensure variety of subfields

4. **Find Test RFPs:**
   - Identify 3 current NSF/NIH/DOE solicitations
   - Ensure Engineering relevance
   - Download full text

### Ready to Implement When Approved

The architecture and plan are ready. Implementation can begin immediately upon your approval to start coding.

---

**Status:** Planning complete, awaiting go-ahead to begin implementation.
