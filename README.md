# Grant Match

> AI-powered grant matching system that automatically connects faculty researchers with relevant funding opportunities through contextualized, personalized recommendations.

## Overview

Grant Match solves a critical challenge in research administration: efficiently matching thousands of faculty members with the right funding opportunities. Rather than manually reviewing RFPs and relying on personal networks, Grant Match uses AI to analyze research profiles and provide specific, reasoned explanations for why each funding opportunity is relevant to each researcher.

**The key innovation:** Not just finding matches, but explaining WHY each match makes sense with specific references to publications, prior work, and RFP requirements.

## The Problem

Research institutions face several challenges in grant matching:

- **Scale:** 1000+ grant-eligible faculty at institutions like Vanderbilt
- **Volume:** Dozens to hundreds of RFPs per year across multiple agencies
- **Manual Process:** Time-consuming, relies on personal networks, limited coverage
- **Missed Opportunities:** Particularly for interdisciplinary or non-obvious matches
- **Generic Communication:** Faculty receive irrelevant opportunities without context

## How It Works

### Core Workflow

1. **RFP Intake**
   - Grant office receives new RFP
   - System extracts essentials: title, agency, deadline, description, requirements

2. **AI-Powered Matching**
   - Reasoning model analyzes RFP against all faculty research profiles
   - Generates ranked matches with specific rationales
   - Identifies alignment points between faculty work and RFP requirements

3. **Personalized Notification**
   - Faculty receive targeted emails with:
     - RFP summary and link
     - Specific explanation of why it matches their work
     - Their current research profile
     - Quick feedback options
   - Example: "Your 2024 paper on neural interfaces (PMID: xxx) directly addresses this RFP's requirement for novel brain-computer interface paradigms (Section 2.3)"

4. **Continuous Improvement**
   - Track feedback on match quality
   - Update research profiles based on corrections
   - Refine matching algorithms over time

## Key Features

### ORCID-Based Profile Generation

- Leverages institutional ORCID IDs for reliable publication tracking
- Monthly automated updates for new publications
- AI-generated research summaries from publication corpus
- Annual faculty validation with real-time correction capability

### High-Quality Matching

- No pre-filtering - analyzes ALL faculty for non-obvious interdisciplinary matches
- Specific rationales citing actual publications and RFP sections
- Relevance scores with suggested approaches
- Cost-effective: ~$40-60 per RFP to process 1000+ faculty

### Feedback-Driven Learning

- Quick feedback: "Good match" / "Not relevant" / "Profile incorrect"
- Easy profile updates via email
- Pattern tracking for continuous improvement
- Self-correcting system through faculty input

## Architecture

### Core Components

1. **Research Profile System**
   - ORCID API integration for publications
   - AI summarization of research areas
   - Continuous updates and validation
   - Faculty-controllable profile management

2. **Matching Engine**
   - Single-stage reasoning approach
   - Processes entire faculty population per RFP
   - Structured output: score, rationale, alignment points

3. **Notification System**
   - Email generation and delivery
   - Feedback collection and tracking
   - Profile update workflows

4. **Learning System**
   - Feedback analytics
   - Prompt refinement
   - Success metrics tracking

## Cost Analysis

**Per-RFP Processing:**
- 1000 faculty × ~$0.04-0.06 = $40-60 per RFP
- Profile updates: ~$600/year
- Infrastructure: ~$1,000/year

**Annual Estimates:**

| RFPs/Year | Total Cost |
|-----------|------------|
| 25        | ~$2,000    |
| 50        | ~$3,000    |
| 100       | ~$5,000    |

**ROI:** A single successful grant award typically exceeds total system cost by orders of magnitude.

## Implementation Roadmap

### Phase 1: Proof of Concept (Weeks 1-3)
- Manually create 20-30 high-quality faculty profiles
- Test matching on 2-3 real RFPs
- Evaluate rationale quality with faculty feedback
- Validate value proposition

### Phase 2: Automation (Weeks 3-6)
- Build ORCID-to-publications pipeline
- Automate profile generation with LLM
- Implement attribution validation
- Test on 50-100 faculty

### Phase 3: End-to-End System (Weeks 6-10)
- Complete matching pipeline
- Design notification templates
- Build feedback tracking system
- Pilot with 50-100 faculty on 3-5 RFPs

### Phase 4: Full Launch (Weeks 10-12)
- Generate profiles for all 1000+ faculty
- Train grant office staff
- Begin processing all RFPs
- Monitor and respond to issues

### Phase 5: Continuous Improvement (Ongoing)
- Monthly feedback analysis
- Quarterly prompt refinement
- Annual faculty validation
- Track success metrics

## Design Principles

**Rationale-First:** The value is explaining WHY, not just finding matches. Faculty appreciate specific, contextualized recommendations.

**Imperfect is OK:** With quick feedback mechanisms, errors self-correct. Don't let perfect be the enemy of good.

**Low Friction:** Quick feedback options and easy profile updates ensure high engagement.

**Transparency:** Always show faculty which profile data was used for matching.

**Faculty Autonomy:** Opt-out friendly, respects researcher independence, augments rather than replaces human judgment.

## Data Sources

- **Publications:** ORCID API (authoritative source via institutional IDs)
- **Grants:** NIH Reporter, NSF Awards APIs
- **Research Statements:** Faculty web pages, department profiles
- **Validation:** Annual faculty review + real-time corrections

## Technical Stack

- AI reasoning models for matching and profile generation
- ORCID API for publication data
- Email delivery system
- Feedback tracking database
- Scheduled automation for profile updates

## Success Metrics

- Match relevance feedback from faculty
- Application rate from matched opportunities
- Successful grant awards attributed to system
- Faculty engagement and profile correction rates
- Interdisciplinary collaboration opportunities discovered

## Getting Started

### Immediate Next Steps

1. **Assess Scale:**
   - Estimate RFP volume per year
   - Verify ORCID coverage for target faculty population

2. **Gather Examples:**
   - Collect 2-3 recent RFPs for testing
   - Identify 20-30 faculty for proof of concept

3. **Build Proof of Concept:**
   - Generate initial faculty profiles
   - Run test matching
   - Validate rationale quality

## Status Dashboard

### 🔴 Live Grant Matches

The MPART @ UIS grant scout runs **daily at 6:00 AM CST** (11:00 UTC) via GitHub Actions.

**Latest Results:** [📊 View mpart_matches.json](./data/mpart_matches.json)

| Metric | Value |
|--------|-------|
| Last Updated | Auto-updated daily |
| Sources | Illinois GATA Portal + SAM.gov |
| Filter | Illinois Higher Education eligible only |
| DeepResearch Trigger | Score > 80 |

### 🚀 For Student Workers

**View the latest matches locally:**

```bash
# Clone or pull the latest
git pull origin main

# Run the student briefing script
python3 src/student_briefing.py
```

This will display:
- Top grant opportunities for MPART
- Recommended Mercenary leads
- Priority scores and deadlines

### 🤖 Automation Status

[![Daily MPART Scout](https://github.com/your-org/grant-match/actions/workflows/daily_mpart_scout.yml/badge.svg)](https://github.com/your-org/grant-match/actions/workflows/daily_mpart_scout.yml)

- **Schedule:** Daily at 6:00 AM CST
- **Manual Trigger:** [Run workflow manually](https://github.com/your-org/grant-match/actions/workflows/daily_mpart_scout.yml)
- **Data Sources:**
  - Illinois GATA Portal (Live web scraping)
  - SAM.gov Federal API

### 📁 Key Files

| File | Description |
|------|-------------|
| `data/mpart_matches.json` | Latest grant matches with Mercenary assignments |
| `data/live_ingestion_results.json` | Full pipeline results from last run |
| `data/gata_live_capture.json` | Raw scraped data from Illinois GATA |
| `src/student_briefing.py` | Student-friendly match viewer |

## Project Status

**Current Phase:** Live automated ingestion with MPART @ UIS

See [brainstorming-notes.md](brainstorming-notes.md) for detailed project planning and [grant-match-demo.md](grant-match-demo.md) for demo preparation notes.

## Contributing

This is currently a research project. For questions or collaboration opportunities, please open an issue.

## License

Copyright 2025. All rights reserved.

---

**Built to solve real problems in research administration through practical AI application.**
