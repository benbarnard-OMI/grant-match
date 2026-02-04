"""
MPART @ UIS Grant Match Dashboard

Streamlit web application for viewing and managing grant matches.

Usage:
    streamlit run src/dashboard/app.py

Environment variables:
    - DATA_GOV_API_KEY: For live SAM.gov queries
    - ANTHROPIC_API_KEY: For AI analysis (optional)
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scout_il import (
    GrantDiscoveryPipeline, 
    GATAWebScraper, 
    SAMSource,
    GrantOpportunity,
    HeuristicScorer
)
from mpart_adapter import MPARTMatchingAdapter, create_adapter


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="MPART @ UIS Grant Matches",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #003366;
        margin-bottom: 0.5rem;
    }
    .subheader {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border-left: 5px solid #003366;
    }
    .match-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .score-high { background: #fee; color: #c33; }
    .score-medium { background: #ffeaa7; color: #d68910; }
    .score-low { background: #dfe6e9; color: #636e72; }
    .lead-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .lead-policy { background: #e3f2fd; color: #1565c0; }
    .lead-data { background: #f3e5f5; color: #7b1fa2; }
    .lead-eval { background: #e8f5e9; color: #2e7d32; }
    .deadline-urgent { color: #e74c3c; font-weight: bold; }
    .deadline-soon { color: #f39c12; font-weight: bold; }
    .deadline-ok { color: #27ae60; }
</style>
""", unsafe_allow_html=True)


def load_matches() -> tuple[List[Dict], Dict]:
    """Load matches from data file."""
    matches_file = Path(__file__).parent.parent.parent / "data" / "mpart_matches.json"
    
    if not matches_file.exists():
        return [], {}
    
    try:
        with open(matches_file) as f:
            data = json.load(f)
        return data.get('matches', []), data.get('metadata', {})
    except Exception as e:
        st.error(f"Error loading matches: {e}")
        return [], {}


def load_historical_data() -> pd.DataFrame:
    """Load historical match data for analytics."""
    history_files = list(Path("data").glob("mpart_matches_*.json"))
    
    if not history_files:
        return pd.DataFrame()
    
    records = []
    for file in sorted(history_files)[-30:]:  # Last 30 days
        try:
            with open(file) as f:
                data = json.load(f)
            date = datetime.fromisoformat(data['metadata']['generated_at'])
            records.append({
                'date': date,
                'total': data['summary']['high_priority'] + data['summary']['medium_priority'],
                'high_priority': data['summary']['high_priority'],
                'medium_priority': data['summary']['medium_priority']
            })
        except:
            continue
    
    return pd.DataFrame(records)


def get_score_color(score: int) -> str:
    """Get CSS class for score."""
    if score >= 80:
        return "score-high"
    elif score >= 50:
        return "score-medium"
    return "score-low"


def get_lead_badge(lead_id: str) -> str:
    """Get HTML for lead badge."""
    badges = {
        'mercenary_policy': ('📋', 'Policy Expert', 'lead-policy'),
        'mercenary_data': ('🔬', 'Data Expert', 'lead-data'),
        'mercenary_eval': ('🏥', 'Rural/Eval Expert', 'lead-eval')
    }
    icon, name, css_class = badges.get(lead_id, ('❓', 'Unassigned', ''))
    return f'<span class="lead-badge {css_class}">{icon} {name}</span>'


def get_deadline_class(deadline_str: str) -> str:
    """Get CSS class for deadline urgency."""
    if not deadline_str:
        return "deadline-ok"
    
    try:
        deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        days_until = (deadline - datetime.now()).days
        
        if days_until < 14:
            return "deadline-urgent"
        elif days_until < 30:
            return "deadline-soon"
        return "deadline-ok"
    except:
        return "deadline-ok"


def render_header():
    """Render page header."""
    st.markdown('<p class="main-header">📊 MPART @ UIS Grant Matches</p>', 
                unsafe_allow_html=True)
    st.markdown('<p class="subheader">Medical Policy Applied Research Team • '
                'University of Illinois Springfield</p>', 
                unsafe_allow_html=True)


def render_summary_stats(matches: List[Dict]):
    """Render summary statistics cards."""
    high_priority = len([m for m in matches if m.get('match_score', 0) >= 80])
    medium_priority = len([m for m in matches if 50 <= m.get('match_score', 0) < 80])
    total = len(matches)
    
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("Total Matches", total)
    with cols[1]:
        st.metric("🔴 High Priority", high_priority, 
                 help="Score >= 80 - Review immediately")
    with cols[2]:
        st.metric("🟡 Medium Priority", medium_priority,
                 help="Score 50-79 - Review if time permits")
    with cols[3]:
        # Count by lead
        lead_counts = {}
        for m in matches:
            lead = m.get('recommended_lead', 'none')
            lead_counts[lead] = lead_counts.get(lead, 0) + 1
        
        st.metric("Leads Assigned", 
                 len([l for l in lead_counts if l != 'none']))


def render_filters() -> Dict:
    """Render filter controls in sidebar."""
    with st.sidebar:
        st.header("🔍 Filters")
        
        min_score = st.slider("Minimum Score", 0, 100, 50)
        
        lead_filter = st.multiselect(
            "Assigned Lead",
            options=["Policy Expert", "Data Expert", "Rural/Eval Expert"],
            default=[]
        )
        
        status_filter = st.multiselect(
            "Review Status",
            options=["New", "Under Review", "Pursuing", "Not Pursuing", "Submitted"],
            default=["New"]
        )
        
        deadline_filter = st.selectbox(
            "Deadline",
            options=["All", "Within 2 weeks", "Within 1 month", "More than 1 month"],
            index=0
        )
        
        st.divider()
        
        st.header("⚡ Actions")
        
        if st.button("🔄 Run Fresh Discovery", type="primary"):
            st.session_state['run_discovery'] = True
        
        if st.button("📧 Send Digest Email"):
            st.session_state['send_digest'] = True
        
        if st.button("📥 Export to Excel"):
            st.session_state['export_excel'] = True
    
    return {
        'min_score': min_score,
        'lead_filter': lead_filter,
        'status_filter': status_filter,
        'deadline_filter': deadline_filter
    }


def filter_matches(matches: List[Dict], filters: Dict) -> List[Dict]:
    """Apply filters to matches."""
    filtered = matches
    
    # Score filter
    filtered = [m for m in filtered if m.get('match_score', 0) >= filters['min_score']]
    
    # Lead filter
    if filters['lead_filter']:
        lead_map = {
            "Policy Expert": "mercenary_policy",
            "Data Expert": "mercenary_data", 
            "Rural/Eval Expert": "mercenary_eval"
        }
        allowed_leads = [lead_map[l] for l in filters['lead_filter']]
        filtered = [m for m in filtered if m.get('recommended_lead') in allowed_leads]
    
    # Deadline filter
    if filters['deadline_filter'] != "All":
        now = datetime.now()
        if filters['deadline_filter'] == "Within 2 weeks":
            cutoff = now + timedelta(days=14)
        elif filters['deadline_filter'] == "Within 1 month":
            cutoff = now + timedelta(days=30)
        else:
            cutoff = now + timedelta(days=30)
            filtered = [m for m in filtered if m.get('deadline') and 
                       datetime.fromisoformat(m['deadline'].replace('Z', '+00:00')) > cutoff]
            return filtered
        
        filtered = [m for m in filtered if m.get('deadline') and 
                   datetime.fromisoformat(m['deadline'].replace('Z', '+00:00')) <= cutoff]
    
    return filtered


def render_match_card(match: Dict):
    """Render a single match card."""
    score = match.get('match_score', 0)
    score_class = get_score_color(score)
    lead = match.get('recommended_lead', '')
    deadline_class = get_deadline_class(match.get('deadline', ''))
    
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.subheader(match.get('grant_title', 'Untitled'))
            st.write(f"**Agency:** {match.get('agency', 'Unknown')}")
            
        with col2:
            st.markdown(f'<span class="score-badge {score_class}">{score}/100</span>', 
                       unsafe_allow_html=True)
            
        with col3:
            st.markdown(get_lead_badge(lead), unsafe_allow_html=True)
        
        deadline = match.get('deadline', 'Not specified')
        st.markdown(f'<span class="{deadline_class}">⏰ Deadline: {deadline}</span>',
                   unsafe_allow_html=True)
        
        with st.expander("View Details"):
            st.write(f"**Why this matches:** {match.get('rationale', 'No rationale')}")
            
            if match.get('alignment_points'):
                st.write("**Key Alignment Points:**")
                for point in match['alignment_points']:
                    st.write(f"• {point}")
            
            st.write(f"**Recommended Action:** {match.get('recommended_action', 'None')}")
            
            # Action buttons
            action_col1, action_col2, action_col3 = st.columns(3)
            with action_col1:
                if st.button("🌐 View Grant", key=f"view_{match['grant_id']}"):
                    st.info(f"Grant URL: {match.get('url', 'Not available')}")
            with action_col2:
                if st.button("✅ Mark Pursuing", key=f"pursue_{match['grant_id']}"):
                    st.success("Marked as pursuing!")
            with action_col3:
                if st.button("❌ Not Relevant", key=f"skip_{match['grant_id']}"):
                    st.info("Marked as not relevant")
        
        st.divider()


def render_matches_table(matches: List[Dict]):
    """Render matches as a sortable table."""
    if not matches:
        st.info("No matches found with current filters.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame([
        {
            'Score': m.get('match_score', 0),
            'Title': m.get('grant_title', ''),
            'Agency': m.get('agency', ''),
            'Deadline': m.get('deadline', ''),
            'Lead': m.get('recommended_lead', '').replace('mercenary_', '').title(),
            'ID': m.get('grant_id', '')
        }
        for m in matches
    ])
    
    st.dataframe(
        df.sort_values('Score', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            'Score': st.column_config.NumberColumn(format="%d/100"),
            'Title': st.column_config.TextColumn(width="large"),
            'Deadline': st.column_config.DateColumn(format="MMM DD, YYYY")
        }
    )


def render_analytics(matches: List[Dict]):
    """Render analytics charts."""
    st.header("📈 Analytics")
    
    # Score distribution
    col1, col2 = st.columns(2)
    
    with col1:
        scores = [m.get('match_score', 0) for m in matches]
        fig = go.Figure(data=[go.Histogram(x=scores, nbinsx=10)])
        fig.update_layout(
            title="Score Distribution",
            xaxis_title="Match Score",
            yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Lead distribution
        leads = {}
        for m in matches:
            lead = m.get('recommended_lead', 'none')
            if lead != 'none':
                leads[lead] = leads.get(lead, 0) + 1
        
        if leads:
            fig = px.pie(
                values=list(leads.values()),
                names=[l.replace('mercenary_', '').title() for l in leads.keys()],
                title="Lead Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Historical trend
    hist_df = load_historical_data()
    if not hist_df.empty:
        st.subheader("30-Day Trend")
        fig = px.line(hist_df, x='date', y=['high_priority', 'medium_priority'],
                     labels={'value': 'Matches', 'variable': 'Priority'},
                     title="Match Volume Over Time")
        st.plotly_chart(fig, use_container_width=True)


def run_live_discovery():
    """Run live grant discovery."""
    with st.spinner("Running grant discovery... This may take 2-3 minutes."):
        try:
            adapter = create_adapter(enable_deep_research=False)
            matches = adapter.discover_and_match()
            
            # Save matches
            adapter.save_matches(matches, "data/mpart_matches.json")
            
            st.success(f"Discovery complete! Found {len(matches)} matches.")
            return matches
            
        except Exception as e:
            st.error(f"Error during discovery: {e}")
            return []


def export_to_excel(matches: List[Dict]):
    """Export matches to Excel file."""
    df = pd.DataFrame([
        {
            'Score': m.get('match_score', 0),
            'Priority': 'High' if m.get('match_score', 0) >= 80 else 'Medium' if m.get('match_score', 0) >= 50 else 'Low',
            'Title': m.get('grant_title', ''),
            'Agency': m.get('agency', ''),
            'Deadline': m.get('deadline', ''),
            'Lead': m.get('recommended_lead', '').replace('mercenary_', '').title(),
            'Rationale': m.get('rationale', ''),
            'Recommended Action': m.get('recommended_action', ''),
            'Grant ID': m.get('grant_id', '')
        }
        for m in matches
    ])
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"mpart_matches_{timestamp}.xlsx"
    filepath = Path("data") / filename
    
    df.to_excel(filepath, index=False, engine='openpyxl')
    
    return filepath


def main():
    """Main application entry point."""
    render_header()
    
    # Load data
    matches, metadata = load_matches()
    
    if not matches:
        st.warning("No matches loaded. Run discovery to find opportunities.")
        if st.button("🔄 Run Discovery Now"):
            matches = run_live_discovery()
    
    # Sidebar filters
    filters = render_filters()
    
    # Handle actions
    if st.session_state.get('run_discovery'):
        matches = run_live_discovery()
        st.session_state['run_discovery'] = False
        st.rerun()
    
    if st.session_state.get('send_digest'):
        st.info("Email digest feature - configure SMTP settings first.")
        st.session_state['send_digest'] = False
    
    if st.session_state.get('export_excel'):
        filepath = export_to_excel(matches)
        with open(filepath, 'rb') as f:
            st.download_button(
                "📥 Download Excel File",
                f,
                file_name=filepath.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        st.session_state['export_excel'] = False
    
    # Filter matches
    filtered_matches = filter_matches(matches, filters)
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📋 Matches", "📊 Analytics", "⚙️ Configuration"])
    
    with tab1:
        render_summary_stats(filtered_matches)
        
        view_mode = st.radio("View Mode", ["Cards", "Table"], horizontal=True)
        
        if view_mode == "Cards":
            for match in filtered_matches[:20]:  # Limit to top 20
                render_match_card(match)
        else:
            render_matches_table(filtered_matches)
    
    with tab2:
        render_analytics(matches)
    
    with tab3:
        st.header("System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Data Sources")
            st.checkbox("Illinois GATA Portal", value=True, disabled=True)
            st.checkbox("SAM.gov (Federal)", value=True, disabled=True)
            st.checkbox("Robert Wood Johnson Foundation", value=False)
            st.checkbox("Commonwealth Fund", value=False)
        
        with col2:
            st.subheader("Notification Settings")
            st.checkbox("Daily Email Digest", value=False)
            st.checkbox("Immediate Alerts (Score > 95)", value=False)
            st.text_input("Notification Email", value="mpart@uis.edu")
        
        st.divider()
        
        st.subheader("Keyword Weights")
        st.json({
            'medicaid': 35,
            'policy monitoring': 25,
            'regulatory analysis': 25,
            'rural health': 15,
            'health services research': 30,
            'health policy': 30
        })
    
    # Footer
    st.divider()
    st.caption(f"Last updated: {metadata.get('generated_at', 'Unknown')} | "
               f"MPART @ UIS Grant Match System")


if __name__ == "__main__":
    main()
