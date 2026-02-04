# Adversarial Analysis: Grant Match for MPART @ UIS

**Date:** 2026-02-04  
**Audience:** Medical Policy Applied Research Team (MPART) Leadership  
**Analyst Perspective:** Critical evaluation for non-technical medical/government researchers  

---

## Executive Summary: The Brutal Truth

This project is a **grant discovery and triage tool** masquerading as an AI-powered matching system. For MPART specifically, it offers **modest value with significant limitations** that need addressing before it becomes truly useful.

**Verdict:** Useful as a monitoring tool, but requires substantial customization to fit MPART's actual workflow.

---

## Part 1: What This Actually Does (Translation for Non-Tech Folks)

### Current State
Every day at 6:00 AM, the system:

1. **Checks Illinois GATA portal** (state grants) - Scrapes the public website
2. **Queries SAM.gov** (federal grants) - Uses an API with keywords like "Medicaid", "policy monitoring", etc.
3. **Scores opportunities** on a 0-100 scale based on keyword matches
4. **Assigns a "Mercenary" lead** (Policy, Data, or Rural/Eval expert)
5. **Saves results** to a JSON file in GitHub
6. **Students can run a script** to see formatted output

### The "Mercenary" Concept
Instead of matching to individual faculty, the system matches to three role-based profiles:
- **Policy Mercenary:** State Medicaid variations, 1115 Waivers, regulatory analysis
- **Data Mercenary:** AI-assisted monitoring, document collection, automation
- **Rural/Eval Mercenary:** Rural health impact, government service evaluation

---

## Part 2: Why MPART Would Care (The Value Proposition)

### ✅ Legitimate Benefits

| Benefit | Explanation |
|---------|-------------|
| **Automated Monitoring** | No need to manually check GATA and SAM.gov daily |
| **Eligibility Filtering** | Automatically filters out grants MPART can't apply for |
| **Lead Assignment** | Suggests which team member should review which opportunity |
| **Daily Cadence** | Runs automatically; students can check results each morning |
| **Cost** | Essentially free (just API costs ~$0) |

### 🔥 The Core Value for MPART

**You have students who can review leads, but they need direction.** This system provides:
1. A daily "inbox" of potentially relevant grants
2. Pre-triaged assignments (Policy/Data/Eval lead)
3. A starting score to prioritize review efforts

---

## Part 3: The Problems (Adversarial Analysis)

### 🔴 Critical Issues

#### 1. **The "AI" is Mostly Just Keyword Matching**

**Reality Check:**
- The "matching" is 90% deterministic keyword scoring
- AI ("DeepResearch") only triggers for scores > 80
- The AI component is currently a **skeleton/stub** (not implemented)

**What this means:**
```python
# This is literally how it works:
if 'medicaid' in grant_text:
    score += 35  # Hardcoded weight
if 'state policy' in grant_text:
    score += 12  # Hardcoded weight
# ... etc
```

**Why this matters for MPART:**
- You'll get false positives (high scores for tangential mentions)
- You'll miss relevant grants that use different terminology
- No semantic understanding of policy research

---

#### 2. **No Integration with MPART's Actual Workflow**

**Current workflow assumption:**
1. System generates JSON file
2. Students run `python src/student_briefing.py`
3. Students manually review text output
4. ??? (No defined next step)

**Missing integrations:**
- ❌ No email notifications when high-priority grants appear
- ❌ No calendar integration for deadlines
- ❌ No CRM/task tracking (Asana, Trello, etc.)
- ❌ No collaboration features (comments, assignments)
- ❌ No document management (storing RFPs, application materials)

**MPART's likely actual workflow:**
- Email alerts when relevant grants appear
- Team discussion about fit
- Assignment to specific team member
- Tracking through application process
- Deadline management

**Gap:** The system stops at "here are some leads" - it doesn't help you *act* on them.

---

#### 3. **The "Mercenary" Framework May Not Match Reality**

**Current model:** Rigid three-category assignment
- Policy Mercenary
- Data Mercenary  
- Rural/Eval Mercenary

**Potential problems:**
- What if a grant spans multiple categories?
- What if your team structure is different?
- What if the same person handles multiple "mercenary" roles?
- No nuance in assignments (it's binary: assigned or not)

**Risk:** Creates artificial silos where collaboration is needed.

---

#### 4. **Limited Data Sources**

**Currently monitoring:**
- Illinois GATA portal (state opportunities)
- SAM.gov (federal opportunities)

**Not monitoring (but probably should be):**
- Foundation grants (Robert Wood Johnson, Commonwealth Fund, etc.)
- NIH funding opportunities (relevant for health policy)
- CMS Innovation Center
- State-specific opportunities beyond Illinois
- Professional association grants (AcademyHealth, etc.)
- Contract opportunities (not just grants)

**Gap:** Health policy research funding often comes from foundations and health-specific sources, not just government RFPs.

---

#### 5. **The Scoring is Opaque and Untuned**

**Current keyword weights (from scout_il.py):**
```python
KEYWORD_WEIGHTS = {
    'medicaid': 35,
    'policy monitoring': 25,
    'regulatory analysis': 25,
    'rural health': 15,
    'policydelta': 20,  # Your internal term
    # ... etc
}
```

**Problems:**
- Who decided these weights?
- Has anyone validated they're correct for MPART?
- What if "Medicaid" appears in a grant about veterinary services? (False positive)
- What about grants that don't use these exact terms but are highly relevant?

**Untested assumption:** The scoring matches MPART's actual priorities.

---

#### 6. **Technical Barrier to Entry**

**To use this system, someone needs to:**
1. Have Python installed
2. Clone a GitHub repository
3. Run command-line scripts
4. Read JSON files or terminal output

**For MPART students:**
- May not have technical backgrounds
- GitHub might be unfamiliar
- Command-line interfaces are intimidating
- Raw JSON is hard to read

**The student briefing script helps, but:**
- Still requires running Python
- Still requires terminal/command line
- No web interface
- No mobile access

---

#### 7. **No Historical Tracking or Analytics**

**What's missing:**
- ❌ No tracking of which grants MPART actually applied for
- ❌ No win/loss rate analysis
- ❌ No feedback loop ("this match was good/bad")
- ❌ No trend analysis ("funding for rural health is increasing")
- ❌ No relationship tracking ("we've applied to this funder before")

**Result:** Every day is a fresh start; no learning from past performance.

---

#### 8. **No Customization Without Coding**

**To change anything, you need to:**
- Edit Python files
- Understand the codebase
- Commit changes to GitHub
- Possibly redeploy

**MPART can't easily:**
- Adjust keyword weights
- Add new funding sources
- Modify the scoring algorithm
- Change the "mercenary" categories
- Add new notification channels

**Lock-in:** You're dependent on technical support for basic configuration changes.

---

## Part 4: Can MPART Actually Use This?

### Current Usability Assessment

| Task | Can MPART Do It? | Difficulty |
|------|------------------|------------|
| View daily grant matches | ⚠️ Partial | Requires running Python script |
| Understand match scores | ✅ Yes | Simple output |
| Assign leads to team | ✅ Yes | Automatic |
| Get email alerts | ❌ No | Not implemented |
| Track application progress | ❌ No | Not implemented |
| Add new keywords | ❌ No | Requires code change |
| Add new funding sources | ❌ No | Requires code change |
| Export to Excel/CSV | ❌ No | JSON only |
| Mobile access | ❌ No | Terminal only |
| Historical analysis | ❌ No | Not implemented |

### Who Can Use This Now?

**Can use effectively:**
- Technical team members comfortable with GitHub and Python
- Students with coding backgrounds
- Anyone willing to learn basic command-line operations

**Will struggle:**
- Non-technical policy researchers
- Team members without GitHub access
- Anyone expecting a web interface or email alerts
- People who need mobile access

---

## Part 5: The Real Questions MPART Should Ask

### Strategic Questions

1. **"How many grants do we actually miss currently?"**
   - If you're already well-connected and don't miss many opportunities, this adds little value
   - If you're missing relevant grants, quantify the problem first

2. **"What's our current workflow for finding grants?"**
   - If it ain't broke, don't fix it
   - If manual monitoring consumes significant time, automation helps

3. **"Do we have someone who can maintain this?"**
   - Someone needs to troubleshoot when it breaks
   - API keys need management
   - Keywords need tuning

4. **"What happens when the developer moves on?"**
   - Current codebase requires Python knowledge
   - No documentation for non-technical users
   - Bus factor = 1

### Operational Questions

5. **"Are these the right funding sources?"**
   - Are foundation grants more relevant than SAM.gov?
   - Should you monitor other states' opportunities?

6. **"Do the 'Mercenary' categories match our team?"**
   - Is this how you actually organize work?
   - Would different categories be more useful?

7. **"What do we do with the output?"**
   - Who reviews the daily matches?
   - How do decisions get made?
   - How does this integrate with actual grant writing?

---

## Part 6: Recommendations

### Immediate (If You Want to Use This Now)

#### 1. **Create a Simple Web Dashboard**
```
Priority: HIGH
Effort: 1-2 days
```
- Streamlit or Flask app that reads the JSON
- Host on free tier (Streamlit Cloud, Heroku, etc.)
- No command line required
- Mobile-friendly

#### 2. **Add Email Notifications**
```
Priority: HIGH
Effort: 1 day
```
- Send daily digest of high-priority matches (score > 80)
- Use SendGrid, Mailgun, or institutional email
- Include direct links to grant opportunities

#### 3. **Export to Excel**
```
Priority: MEDIUM
Effort: 2 hours
```
- Add `--export-excel` flag to student_briefing.py
- Generate .xlsx files students can open
- More familiar than terminal output

#### 4. **Validate Keywords with MPART**
```
Priority: HIGH
Effort: 1 day
```
- Review past successful grants
- Identify common terms
- Adjust weights based on actual MPART priorities
- Add foundation-specific keywords

### Medium-Term (Next 1-3 Months)

#### 5. **Add Foundation Sources**
```
Priority: HIGH
Effort: 2-3 days
```
- Robert Wood Johnson Foundation
- Commonwealth Fund
- Kaiser Family Foundation
- AcademyHealth
- State Health Access Data Assistance Center (SHADAC)

#### 6. **Build Feedback Loop**
```
Priority: MEDIUM
Effort: 2-3 days
```
- Track which matches MPART actually pursued
- Log wins/losses
- Use feedback to tune scoring
- Monthly report on match quality

#### 7. **Integration with Grant Management**
```
Priority: MEDIUM
Effort: 3-5 days
```
- Export to Asana/Trello/Monday.com
- Calendar integration for deadlines
- Document storage for RFPs
- Assignment tracking

### Long-Term (3-6 Months)

#### 8. **True AI Matching**
```
Priority: LOW (currently skeleton implementation)
Effort: 1-2 weeks
```
- Implement actual LLM calls for deep research
- Semantic matching (not just keywords)
- Rationale generation with explanations

#### 9. **Multi-State Expansion**
```
Priority: Depends on MPART scope
Effort: 1 week
```
- Add other state grant portals
- Federal agency-specific monitoring
- Regional foundation tracking

#### 10. **User-Friendly Admin Interface**
```
Priority: MEDIUM
Effort: 1-2 weeks
```
- Web UI for adjusting keywords
- Add/remove funding sources
- Configure thresholds
- No code required

---

## Part 7: The Honest Bottom Line

### What This System IS Good For

1. **Automated daily monitoring** of known funding sources
2. **Basic triage** with keyword scoring
3. **Lead assignment** to team members
4. **Student worker enablement** (with technical support)
5. **Cost-effective operation** (free infrastructure)

### What This System IS NOT Good For

1. **Comprehensive coverage** of health policy funding
2. **Sophisticated matching** (it's keyword-based)
3. **End-to-end workflow** (stops at discovery)
4. **Non-technical users** (requires coding knowledge to use/modify)
5. **Historical tracking** (no analytics or learning)

### Should MPART Use This?

**YES, if:**
- You have someone technical who can maintain it
- You're currently missing grants due to lack of monitoring
- You want a starting point for grant discovery
- You're willing to iterate and improve it

**NO, if:**
- You need a turnkey solution
- You don't have technical support
- Your current grant discovery process works fine
- You need comprehensive foundation/health-specific funding coverage

### Recommendation

**Use it as a foundation, but plan to invest 1-2 weeks of development time to make it truly useful:**

1. Add web dashboard + email notifications (usability)
2. Add foundation funding sources (coverage)
3. Validate and tune keywords (accuracy)
4. Build feedback loop (learning)

Without these improvements, it's a **technical demo** that produces daily reports, not a **production tool** that transforms MPART's grant acquisition process.

---

## Appendix: Questions to Ask the Developer

1. "What's the false positive rate? Have you tested this against known relevant/irrelevant grants?"
2. "What happens when the GATA website changes layout? How often does the scraper break?"
3. "Can you show me an example of a grant this system found that MPART would have missed?"
4. "How do we add foundation funding sources?"
5. "What's the plan for maintaining this when you're not available?"
6. "Can we get email alerts instead of checking GitHub?"
7. "How do we track which grants we actually applied for and won?"

---

**End of Analysis**
