# Identity Refactor: OMI → MPART @ UIS

## Summary

Completed global identity correction from "OMI" / "Office of Medicaid Innovation" to  
"MPART @ UIS" (Medical Policy Applied Research Team at University of Illinois Springfield).

## Files Changed

### 1. data/faculty_from_fis.json
**Changes:**
- `organization`: "Office of Medicaid Innovation (OMI)" → "MPART @ UIS"
- `faculty[0].id`: "omi_mpart_team_001" → "mpart_uis_team_001"
- `faculty[0].name`: "OMI Research Team (MPART)" → "MPART @ UIS Research Team"
- `faculty[0].department`: "Office of Medicaid Innovation (OMI)" → "MPART @ UIS"
- `faculty[0].department_code`: "omi" → "mpart"
- `faculty[0].title`: "Office of Medicaid Innovation Research Team" → "Medical Policy Applied Research Team"
- `faculty[0].email`: "omi@uis.edu" → "mpart@uis.edu"
- `faculty[0].data_source`: "OMI_MPART_Team_Profile.json" → "MPART_UIS_Team_Profile.json"
- Added `organization_full` to metadata
- Added `department_full` to faculty entry

### 2. data/department_inventory.json
**Changes:**
- `metadata.source`: "Office of Medicaid Innovation (OMI) - UI Springfield" → "MPART @ UIS (Medical Policy Applied Research Team...)"
- `departments[0].id`: "omi" → "mpart"
- `departments[0].name`: "Office of Medicaid Innovation (OMI)" → "MPART @ UIS"
- `departments[0].full_name`: "Office of Medicaid Innovation" → "Medical Policy Applied Research Team at University of Illinois Springfield"
- Added `short_name`: "MPART"

### 3. src/scout_il.py (Enhanced)
**Identity Changes:**
- Module docstring: "OMI" → "MPART @ UIS"
- Comments: "OMI" → "MPART @ UIS"
- CLI header: "for OMI" → "for MPART @ UIS"
- Factory function: `create_omi_pipeline()` → `create_mpart_pipeline()`

**New Features Added:**
- `HeuristicScorer` class: Deterministic keyword scoring (0-100)
  - Keywords: 'medicaid'(30), '1115 waiver'(25), 'lcnc'(20), 'applied research'(15)
- `pre_filter()` method: Pure Python filtering (no AI)
  - Rejects past deadlines
  - Requires 'Illinois' or 'IL' in text
  - Requires 'Higher Education' or 'Public Universities' eligibility
- `process_grant()` method: Pipeline processing with pre-filter + scoring
- `get_qualified_opportunities()` method: Returns grants with score >= 50
- `--test-prefilter` CLI flag for testing filter logic

### 4. src/mpart_adapter.py (NEW FILE)
**Purpose:** Decouple MPART @ UIS matching logic from Vanderbilt upstream

**Components:**
- `ResearchDepth` enum: PREFILTER_ONLY, HEURISTIC_ONLY, DEEP_RESEARCH
- `MatchResult` dataclass: Structured match output
- `MPARTProfileLoader` class: Loads faculty profile from JSON
- `DeepResearchEngine` class: AI analysis (triggered only if keyword_score > 50)
- `MPARTMatchingAdapter` class: Main orchestrator
  - Tiered workflow: pre-filter → heuristic score → AI deep research (conditional)
  - Deep research threshold: 50 (configurable)
  - Methods: `initialize()`, `match_grant()`, `match_grants()`, `discover_and_match()`

**AI Trigger Condition:**
```python
if keyword_score > DEEP_RESEARCH_THRESHOLD:  # 50
    perform_deep_research(grant, profile)
```

## Test Results

### Pre-filter Tests
```
✓ PASS | Illinois Medicaid Innovation Grant for Universities
✗ FAIL | Old Illinois Grant (deadline in past)
✗ FAIL | Federal Medicaid Grant (no Illinois reference)
✗ FAIL | Illinois Community Grant (not eligible for higher ed)
```

### Matching Tests
```
● IL-001 | Score: 100/100 | deep_research (all keywords matched)
● IL-003 | Score: 100/100 | deep_research (all keywords matched)
✗ IL-002 | Score: 0/100 | prefilter_only (ineligible audience)
✗ FED-001 | Score: 0/100 | prefilter_only (no Illinois reference)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Grant Discovery                          │
│              (Illinois GATA, Grants.gov, CMS)               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              GrantDiscoveryPipeline                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  pre_filter() - Deterministic, No AI               │   │
│  │  • Deadline in future?                             │   │
│  │  • Contains 'Illinois' or 'IL'?                    │   │
│  │  • Eligible for Higher Ed/Public Universities?     │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  HeuristicScorer.score() - Deterministic, No AI    │   │
│  │  • Keyword matching with weights                   │   │
│  │  • Output: 0-100 score                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              MPARTMatchingAdapter                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  IF keyword_score > 50:                            │   │
│  │     DeepResearchEngine.analyze() ← AI CALL        │   │
│  │  ELSE:                                             │   │
│  │     Heuristic-only match                          │   │
│  └─────────────────────────────────────────────────────┘   │
│                            │                                │
│                            ▼                                │
│                   MatchResult output                        │
└─────────────────────────────────────────────────────────────┘
```

## Commands

### Test Pre-filter Logic
```bash
python3 src/scout_il.py --test-prefilter
```

### Run Sample Matches
```bash
python3 src/mpart_adapter.py --test
```

### Dry Run Discovery
```bash
python3 src/scout_il.py --dry-run
```

## No Remaining OMI References

Verified: All references to "OMI" and "Office of Medicaid Innovation" have been  
replaced with "MPART @ UIS" and "Medical Policy Applied Research Team" across all  
data files, source code, and documentation.
