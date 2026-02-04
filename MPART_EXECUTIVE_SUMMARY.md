# MPART @ UIS Grant Match System
## Executive Summary for Leadership

---

## What Is This?

An **automated grant discovery system** that scans Illinois and federal funding opportunities daily and alerts MPART to relevant matches.

**Think of it as:** A robot that reads GATA and SAM.gov every morning so your team doesn't have to.

---

## Current Capabilities

| Feature | Status | Notes |
|---------|--------|-------|
| Daily automated scanning | ✅ Working | GATA + SAM.gov |
| Keyword-based scoring | ✅ Working | 0-100 scale |
| Lead assignment | ✅ Working | Policy/Data/Rural |
| Email alerts | ❌ Not implemented | Must check GitHub |
| Web interface | ❌ Not implemented | Command line only |
| Foundation sources | ❌ Not implemented | Only government |

---

## How It Works (Simple)

```
Every day at 6:00 AM
         │
         ▼
┌──────────────────┐
│ Scan GATA portal │
│ Query SAM.gov    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Score each grant │
│ (keyword match)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Save to GitHub   │
│ Assign to lead   │
└──────────────────┘
```

**Students check results:** `python src/student_briefing.py`

---

## What MPART Gets

### Daily Output Example

```
📊 MPART @ UIS STUDENT BRIEFING

📈 SUMMARY
  Last Updated: 2026-02-04 06:00:00
  Total Leads: 7
  Passed Filter: 5
  High Priority: 2 (Score > 80)

🎯 HIGH PRIORITY MATCHES

  #1 [████████░░] 92/100
     📌 Illinois Medicaid PolicyDelta Analysis
     🏢 Illinois HFS
     ⏰ Deadline: Mar 15, 2026
     📋 Recommended Lead: Policy Expert
     ✓ Key Alignment: 1115 Waiver experience

  #2 [███████░░░] 85/100
     📌 National Policy Tracker Implementation
     🏢 Illinois DHS
     ⏰ Deadline: Apr 30, 2026
     🔬 Recommended Lead: Data/AI Expert
     ✓ Key Alignment: Regulatory monitoring
```

---

## The Good News

1. **It's automated** - Runs daily without intervention
2. **It's free** - No licensing costs
3. **It filters** - Only shows Illinois-eligible, higher-ed opportunities
4. **It assigns** - Suggests which team member should review
5. **It scores** - Prioritizes so you review high-matches first

---

## The Challenges

### Problem 1: Technical Barrier
- Must use command line / GitHub
- No email notifications
- No web interface
- Students need technical skills

**Fix:** Add web dashboard (1 week effort)

### Problem 2: Limited Sources
- Only government grants (GATA, SAM.gov)
- Missing foundations (RWJF, Commonwealth, etc.)
- Missing health-specific sources

**Fix:** Add foundation scrapers (1 week effort)

### Problem 3: No Workflow Integration
- Doesn't track applications
- No deadline reminders
- No collaboration features
- No historical reporting

**Fix:** Add tracking and notifications (1 week effort)

---

## Investment Required

### To Make This Production-Ready

| Component | Effort | Cost |
|-----------|--------|------|
| Web dashboard | 2-3 days | $0 |
| Email alerts | 4 hours | $0 |
| Foundation sources | 3-4 days | $0 |
| Keyword tuning | 1 day | $0 |
| **Total** | **~2 weeks** | **$0** |

### Ongoing Maintenance
- Monitor for breakages: ~2 hours/month
- Keyword updates: ~1 hour/month
- Student training: ~1 hour (one-time)

---

## Decision Framework

### ✅ Use This If:
- You have someone who can spend 2 weeks on improvements
- You're currently missing grant opportunities
- You want automated monitoring
- You can tolerate a "beta" experience initially

### ❌ Don't Use This If:
- You need a turnkey solution today
- You don't have technical support
- Your current grant discovery process works fine
- You need comprehensive foundation coverage immediately

---

## Recommendation

**Adopt with caveats.**

This system provides **genuine value** (automated monitoring) but needs **2 weeks of polish** to be truly usable by non-technical staff.

### Immediate Actions (If Proceeding)

1. **Week 1:** Add email notifications + Excel export
2. **Week 2:** Add RWJF and Commonwealth Fund sources
3. **Week 3:** Deploy web dashboard
4. **Week 4:** Train team and gather feedback

### Alternative: Wait and See

If technical resources aren't available, consider:
- Continue manual monitoring for now
- Revisit when student developer is available
- Consider commercial grant databases (GrantStation, Foundation Directory)

---

## Questions for MPART Team

1. **How do you find grants now?** (If it's working, this may not be needed)
2. **Who would maintain this?** (Needs 2-4 hours/month)
3. **Are foundation grants important?** (Currently not covered)
4. **Can students use command line?** (If not, need web dashboard)
5. **What's the pain point?** (Quantify the problem before solving)

---

## Bottom Line

| Aspect | Assessment |
|--------|------------|
| **Concept** | ✅ Solid - automated grant monitoring is valuable |
| **Current Implementation** | ⚠️ Functional but rough - needs polish |
| **Fit for MPART** | ✅ Good - aligned with research focus |
| **Ready for Production** | ❌ No - needs 2 weeks development |
| **Worth the Investment** | ✅ Yes - if technical resources available |

**Verdict:** A worthwhile foundation that needs finishing work before MPART can fully benefit.

---

## Next Steps

1. **Review adversarial analysis** (`MPART_ADVERSARIAL_ANALYSIS.md`)
2. **Review implementation roadmap** (`MPART_IMPLEMENTATION_ROADMAP.md`)
3. **Assign technical resource** for 2-week development sprint
4. **Validate keywords** with MPART research priorities
5. **Decide:** Proceed with improvements or pursue alternatives

---

**Document Version:** 1.0  
**Date:** 2026-02-04  
**Prepared for:** MPART @ UIS Leadership
