# MPART @ UIS Implementation Roadmap

**Purpose:** Practical guide for adapting Grant Match to MPART's specific needs  
**Audience:** MPART leadership and technical support  
**Status:** Ready for review and prioritization  

---

## Current State vs. MPART Needs

### What You Have Now
- ✅ Automated daily scanning of Illinois GATA + SAM.gov
- ✅ Basic keyword scoring (0-100 scale)
- ✅ Lead assignment (Policy/Data/Eval)
- ✅ GitHub-based automation
- ✅ Student briefing script (command-line)

### What You Need for Production Use
- ⏳ Email notifications
- ⏳ Web dashboard (no command line)
- ⏳ Foundation funding sources
- ⏳ Excel export
- ⏳ Historical tracking

---

## Phase 1: Immediate Wins (Week 1)

### Task 1.1: Enable Email Notifications
**Priority:** CRITICAL  
**Effort:** 4 hours  
**Impact:** Makes system actually usable

**Implementation:**
```python
# Add to src/scout_il.py
import smtplib
from email.mime.text import MIMEText

def send_daily_digest(high_priority_matches):
    """Send email when high-priority grants are found."""
    msg = MIMEText(format_email_body(high_priority_matches))
    msg['Subject'] = f"MPART Grant Alert: {len(high_priority_matches)} High-Priority Matches"
    msg['From'] = "grants@uis.edu"
    msg['To'] = "mpart-team@uis.edu"
    
    with smtplib.SMTP('smtp.uis.edu') as server:
        server.send_message(msg)
```

**Configuration needed:**
- SMTP server credentials
- Recipient list (MPART team + students)
- Threshold for "high priority" (default: score > 80)

---

### Task 1.2: Excel Export for Students
**Priority:** HIGH  
**Effort:** 2 hours  
**Impact:** Removes technical barrier

**Implementation:**
```bash
# New command
python src/student_briefing.py --excel
# Creates: data/mpart_matches_2026-02-04.xlsx
```

**Output columns:**
| Score | Title | Agency | Deadline | Lead | Rationale | URL |
|-------|-------|--------|----------|------|-----------|-----|

Students open Excel instead of running terminal commands.

---

### Task 1.3: Validate Keywords with MPART
**Priority:** HIGH  
**Effort:** 1 day  
**Impact:** Improves match quality

**Process:**
1. Review last 10 grants MPART applied for
2. Extract common terms
3. Compare to current keywords
4. Adjust weights

**Current keywords to review:**
```python
KEYWORD_WEIGHTS = {
    'medicaid': 35,              # ✓ Core - keep high
    'policy monitoring': 25,     # ? Verify MPART uses this term
    'regulatory analysis': 25,   # ? May be too academic
    'rural health': 15,          # ✓ Keep
    'policydelta': 20,           # ✓ Internal term
    'national policy tracker': 18,  # ? Verify
    # Missing: 'health services research', 'health policy', etc.
}
```

**Suggested additions based on health policy field:**
- 'health services research' (30)
- 'health policy' (30)
- 'health equity' (20)
- 'community health' (15)
- '1115 waiver' (25) - already have, verify weight

---

## Phase 2: Foundation Sources (Week 2)

### Task 2.1: Add Robert Wood Johnson Foundation
**Priority:** HIGH  
**Effort:** 1 day  
**Impact:** Major health policy funder

**Source:** https://www.rwjf.org/en/grants/funding-opportunities.html

**Implementation:**
```python
class RWJFSource(GrantSource):
    """Robert Wood Johnson Foundation scraper."""
    URL = "https://www.rwjf.org/en/grants/funding-opportunities.html"
    
    def discover(self):
        # Scrape current opportunities
        # Filter for research/policy grants
        pass
```

---

### Task 2.2: Add Commonwealth Fund
**Priority:** HIGH  
**Effort:** 1 day  
**Impact:** Health policy research focus

**Source:** https://www.commonwealthfund.org/grants-and-fellowships

---

### Task 2.3: Add AcademyHealth
**Priority:** MEDIUM  
**Effort:** 1 day  
**Impact:** Health services research

**Source:** https://www.academyhealth.org/career/funding-opportunities

---

### Task 2.4: Add SHADAC
**Priority:** MEDIUM  
**Effort:** 4 hours  
**Impact:** State health policy data

**Source:** https://www.shadac.org/about/employment-and-rfps

---

## Phase 3: Web Dashboard (Week 3-4)

### Task 3.1: Build Streamlit Dashboard
**Priority:** HIGH  
**Effort:** 2-3 days  
**Impact:** Eliminates technical barrier

**Features:**
- View daily matches in browser
- Filter by score, lead, deadline
- Sort and search
- Download Excel
- Mobile-responsive

**URL:** https://mpart-grants.streamlit.app (example)

**Code structure:**
```python
# src/dashboard.py
import streamlit as st

st.title("MPART @ UIS Grant Matches")

# Load data
matches = load_matches()

# Filters
min_score = st.slider("Minimum Score", 0, 100, 50)
selected_lead = st.selectbox("Lead", ["All", "Policy", "Data", "Rural/Eval"])

# Display
for match in filtered_matches:
    st.card(match)
```

---

### Task 3.2: Deploy Dashboard
**Priority:** HIGH  
**Effort:** 2 hours  
**Impact:** Makes system accessible

**Options:**
1. **Streamlit Cloud** (free): https://streamlit.io/cloud
2. **GitHub Pages** (free, static): Export HTML daily
3. **UIS hosting**: If available

**Recommendation:** Streamlit Cloud - free, auto-updates, minimal maintenance.

---

## Phase 4: Workflow Integration (Week 5-6)

### Task 4.1: Track Application Decisions
**Priority:** MEDIUM  
**Effort:** 2 days  
**Impact:** Enables learning/feedback

**Add to match JSON:**
```json
{
  "mpart_review": {
    "status": "pursuing|not_pursuing|submitted|awarded|declined",
    "reviewed_by": "name",
    "reviewed_date": "2026-02-04",
    "notes": "...",
    "assigned_lead": "actual person"
  }
}
```

**Simple web form or Excel template for tracking.**

---

### Task 4.2: Generate Monthly Reports
**Priority:** MEDIUM  
**Effort:** 1 day  
**Impact:** Shows value over time

**Report includes:**
- Total opportunities discovered
- Breakdown by source
- MPART's response rate
- Win/loss rate
- Trends (funding up/down)

---

## Phase 5: Advanced Features (Month 2-3)

### Task 5.1: Implement True AI Analysis
**Priority:** LOW  
**Effort:** 1 week  
**Impact:** Better rationales and recommendations

**Current state:** Skeleton implementation (not working)

**Implementation:**
```python
# Use Claude API for high-priority matches
def deep_research_analysis(grant, profile):
    prompt = f"""
    Analyze this grant for MPART @ UIS:
    
    Grant: {grant.title}
    Description: {grant.description}
    
    MPART focuses on: {profile.research_areas}
    
    Provide:
    1. Relevance assessment (1-10)
    2. Specific alignment points
    3. Competitive positioning
    4. Recommended approach
    """
    
    return call_claude_api(prompt)
```

**Cost:** ~$0.05-0.10 per analysis × ~5 high-priority grants/day = ~$15/month

---

### Task 5.2: Calendar Integration
**Priority:** LOW  
**Effort:** 2 days  
**Impact:** Deadline management

**Options:**
- Export .ics files
- Google Calendar API integration
- Outlook calendar invites

---

### Task 5.3: Multi-State Expansion
**Priority:** Depends on scope  
**Effort:** 1 week per state  
**Impact:** Broader opportunity discovery

**If MPART works beyond Illinois:**
- Missouri grants
- Indiana grants
- Federal opportunities beyond SAM.gov

---

## Implementation Priorities

### Must-Have (Do First)
1. ✅ Email notifications
2. ✅ Excel export
3. ✅ Keyword validation
4. ✅ RWJF source

### Should-Have (Do Soon)
5. Web dashboard
6. Commonwealth Fund source
7. Decision tracking
8. AcademyHealth source

### Nice-to-Have (Do Later)
9. True AI analysis
10. Calendar integration
11. Multi-state expansion
12. Monthly reports

---

## Resource Requirements

### Technical Resources
| Role | Time Needed | Notes |
|------|-------------|-------|
| Python Developer | 2-3 weeks | Can be student/intern |
| MPART Staff | 4-8 hours | Keyword validation, testing |
| System Admin | 2 hours | API keys, deployment |

### Ongoing Costs
| Item | Monthly Cost | Notes |
|------|--------------|-------|
| GitHub | $0 | Free tier sufficient |
| Streamlit Cloud | $0 | Free tier sufficient |
| Email/SMTP | $0 | Use UIS infrastructure |
| Claude API | $15-30 | If AI analysis enabled |
| SAM.gov API | $0 | Free |

### One-Time Costs
- Initial development: ~2-3 weeks
- Testing and validation: ~1 week
- Documentation and training: ~2 days

---

## Success Metrics

### Month 1 Targets
- [ ] System sends daily email digest
- [ ] Students can view matches without command line
- [ ] Foundation sources added
- [ ] No grants with score >90 are missed

### Month 3 Targets
- [ ] 50+ relevant opportunities identified/month
- [ ] MPART applies to 10+ discovered grants
- [ ] Win rate on system-discovered grants tracked
- [ ] Team reports time savings vs. manual monitoring

### Month 6 Targets
- [ ] System discovers grants MPART would have missed
- [ ] ROI positive (time saved > development cost)
- [ ] Workflow fully integrated with MPART processes
- [ ] Student onboarding takes <30 minutes

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Technical person leaves | Medium | High | Document everything; use simple tools |
| Data source changes | Medium | Medium | Monitor for breakages; have fallback |
| Low match quality | Medium | Medium | Regular keyword tuning; feedback loop |
| Team doesn't adopt | Medium | High | Make it easier than current process |
| API costs increase | Low | Low | Use free tiers; monitor usage |

---

## Quick Start Checklist

### Week 1
- [ ] Set up email notifications
- [ ] Test with MPART team
- [ ] Validate keywords
- [ ] Create Excel export

### Week 2
- [ ] Add RWJF source
- [ ] Add Commonwealth Fund
- [ ] Test foundation sources
- [ ] Document process for students

### Week 3
- [ ] Build Streamlit dashboard
- [ ] Deploy to Streamlit Cloud
- [ ] Train team on dashboard
- [ ] Get feedback

### Week 4
- [ ] Add decision tracking
- [ ] Create monthly report template
- [ ] Review and iterate
- [ ] Plan next phase

---

## Contact & Support

**Questions about this roadmap:**
- Review adversarial analysis for context
- Check AUTOMATION_SUMMARY.md for technical details
- Check LIVE_INGESTION_SUMMARY.md for current capabilities

**Technical support:**
- GitHub repository: [your-repo-url]
- Issues: Create GitHub issue for bugs/features
- Documentation: See docs/ folder

---

**End of Roadmap**
