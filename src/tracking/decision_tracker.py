"""
Decision tracking system for MPART grant matches.

Tracks decisions, status changes, and outcomes for grant opportunities.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


logger = logging.getLogger(__name__)


class DecisionStatus(Enum):
    """Status of a grant decision."""
    NEW = "new"                          # Just discovered
    UNDER_REVIEW = "under_review"        # Being evaluated
    PURSUING = "pursuing"                # Decision to apply made
    NOT_PURSUING = "not_pursuing"        # Decision not to apply
    APPLICATION_DRAFT = "application_draft"  # Working on application
    SUBMITTED = "submitted"              # Application submitted
    AWARDED = "awarded"                  # Grant awarded
    DECLINED = "declined"                # Grant declined
    WITHDRAWN = "withdrawn"              # Application withdrawn


@dataclass
class GrantDecision:
    """Tracks the decision and status for a grant opportunity."""
    grant_id: str
    grant_title: str
    status: DecisionStatus
    decided_by: str = ""
    decision_date: str = ""
    notes: str = ""
    assigned_lead: str = ""
    match_score: int = 0
    application_deadline: str = ""
    agency: str = ""
    estimated_amount: str = ""
    actual_amount: str = ""
    submission_date: str = ""
    award_date: str = ""
    feedback: str = ""
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if not self.decision_date:
            self.decision_date = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GrantDecision':
        """Create from dictionary."""
        data = data.copy()
        data['status'] = DecisionStatus(data.get('status', 'new'))
        return cls(**data)


class DecisionTracker:
    """
    Tracks decisions and workflow for grant opportunities.
    
    Provides:
    - Status tracking from discovery to award
    - Historical record of decisions
    - Analytics on win rates and outcomes
    - Collaboration features (assignments, notes)
    """
    
    DEFAULT_DATA_FILE = "data/grant_decisions.json"
    
    def __init__(self, data_file: Optional[str] = None):
        self.data_file = Path(data_file or self.DEFAULT_DATA_FILE)
        self.decisions: Dict[str, GrantDecision] = {}
        self._load_data()
    
    def _load_data(self):
        """Load existing decision data."""
        if self.data_file.exists():
            try:
                with open(self.data_file) as f:
                    data = json.load(f)
                
                for item in data.get('decisions', []):
                    decision = GrantDecision.from_dict(item)
                    self.decisions[decision.grant_id] = decision
                
                logger.info(f"Loaded {len(self.decisions)} decisions")
            except Exception as e:
                logger.error(f"Error loading decisions: {e}")
    
    def _save_data(self):
        """Save decision data to file."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'total_decisions': len(self.decisions)
            },
            'decisions': [d.to_dict() for d in self.decisions.values()]
        }
        
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def track_match(self, match: Dict[str, Any]) -> GrantDecision:
        """
        Start tracking a new grant match.
        
        Args:
            match: Match dictionary from the matching system
            
        Returns:
            GrantDecision for the match
        """
        grant_id = match.get('grant_id')
        
        if grant_id in self.decisions:
            # Already tracking
            return self.decisions[grant_id]
        
        decision = GrantDecision(
            grant_id=grant_id,
            grant_title=match.get('grant_title', ''),
            status=DecisionStatus.NEW,
            assigned_lead=match.get('recommended_lead', ''),
            match_score=match.get('match_score', 0),
            application_deadline=match.get('deadline', ''),
            agency=match.get('agency', '')
        )
        
        self.decisions[grant_id] = decision
        self._save_data()
        
        logger.info(f"Started tracking decision for {grant_id}")
        return decision
    
    def update_status(self, grant_id: str, status: DecisionStatus,
                     decided_by: str = "", notes: str = "") -> Optional[GrantDecision]:
        """
        Update the status of a grant decision.
        
        Args:
            grant_id: ID of the grant
            status: New status
            decided_by: Person making the decision
            notes: Notes about the decision
            
        Returns:
            Updated GrantDecision or None if not found
        """
        if grant_id not in self.decisions:
            logger.warning(f"No decision found for {grant_id}")
            return None
        
        decision = self.decisions[grant_id]
        old_status = decision.status
        decision.status = status
        decision.decided_by = decided_by or decision.decided_by
        decision.decision_date = datetime.now().isoformat()
        
        if notes:
            decision.notes = f"{decision.notes}\n[{datetime.now().strftime('%Y-%m-%d')}] {notes}".strip()
        
        self._save_data()
        
        logger.info(f"Updated {grant_id}: {old_status.value} -> {status.value}")
        return decision
    
    def assign_lead(self, grant_id: str, lead: str) -> bool:
        """Assign a specific person as lead."""
        if grant_id not in self.decisions:
            return False
        
        self.decisions[grant_id].assigned_lead = lead
        self._save_data()
        return True
    
    def add_note(self, grant_id: str, note: str) -> bool:
        """Add a note to a decision."""
        if grant_id not in self.decisions:
            return False
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        self.decisions[grant_id].notes += f"\n[{timestamp}] {note}"
        self._save_data()
        return True
    
    def record_submission(self, grant_id: str, submission_date: str = "") -> bool:
        """Record that an application was submitted."""
        if grant_id not in self.decisions:
            return False
        
        decision = self.decisions[grant_id]
        decision.status = DecisionStatus.SUBMITTED
        decision.submission_date = submission_date or datetime.now().isoformat()
        self._save_data()
        return True
    
    def record_outcome(self, grant_id: str, awarded: bool,
                      amount: str = "", feedback: str = "") -> bool:
        """Record the outcome of a grant application."""
        if grant_id not in self.decisions:
            return False
        
        decision = self.decisions[grant_id]
        decision.status = DecisionStatus.AWARDED if awarded else DecisionStatus.DECLINED
        decision.award_date = datetime.now().isoformat()
        decision.actual_amount = amount
        decision.feedback = feedback
        self._save_data()
        return True
    
    def get_decision(self, grant_id: str) -> Optional[GrantDecision]:
        """Get a specific decision."""
        return self.decisions.get(grant_id)
    
    def get_active_applications(self) -> List[GrantDecision]:
        """Get all grants currently being pursued."""
        active_statuses = [DecisionStatus.PURSUING, DecisionStatus.APPLICATION_DRAFT]
        return [d for d in self.decisions.values() if d.status in active_statuses]
    
    def get_pending_submissions(self) -> List[GrantDecision]:
        """Get grants with upcoming deadlines."""
        return [d for d in self.decisions.values() 
                if d.status in [DecisionStatus.PURSUING, DecisionStatus.APPLICATION_DRAFT]]
    
    def get_win_rate(self) -> Dict[str, Any]:
        """Calculate win rate statistics."""
        submitted = [d for d in self.decisions.values() 
                    if d.status in [DecisionStatus.AWARDED, DecisionStatus.DECLINED]]
        
        awarded = [d for d in submitted if d.status == DecisionStatus.AWARDED]
        
        total_awarded = sum(float(d.actual_amount.replace('$', '').replace(',', '')) 
                          for d in awarded if d.actual_amount)
        
        return {
            'total_submitted': len(submitted),
            'awarded': len(awarded),
            'declined': len(submitted) - len(awarded),
            'win_rate': len(awarded) / len(submitted) * 100 if submitted else 0,
            'total_awarded_amount': total_awarded
        }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics."""
        status_counts = {}
        for status in DecisionStatus:
            count = len([d for d in self.decisions.values() if d.status == status])
            status_counts[status.value] = count
        
        lead_counts = {}
        for d in self.decisions.values():
            lead = d.assigned_lead or "Unassigned"
            lead_counts[lead] = lead_counts.get(lead, 0) + 1
        
        return {
            'total_tracked': len(self.decisions),
            'status_breakdown': status_counts,
            'lead_distribution': lead_counts,
            'win_rate': self.get_win_rate()
        }


def integrate_with_matches(matches_file: str = "data/mpart_matches.json") -> List[GrantDecision]:
    """
    Convenience function to start tracking all current matches.
    
    Args:
        matches_file: Path to matches JSON file
        
    Returns:
        List of GrantDecisions created
    """
    from pathlib import Path
    
    tracker = DecisionTracker()
    
    with open(matches_file) as f:
        data = json.load(f)
    
    decisions = []
    for match in data.get('matches', []):
        decision = tracker.track_match(match)
        decisions.append(decision)
    
    return decisions


if __name__ == '__main__':
    # Test the decision tracker
    tracker = DecisionTracker()
    
    # Simulate some decisions
    test_match = {
        'grant_id': 'TEST-001',
        'grant_title': 'Test Grant',
        'match_score': 85,
        'deadline': '2026-06-01',
        'agency': 'Test Agency',
        'recommended_lead': 'mercenary_policy'
    }
    
    decision = tracker.track_match(test_match)
    print(f"Created decision: {decision.grant_id} - {decision.status.value}")
    
    tracker.update_status('TEST-001', DecisionStatus.PURSUING, 
                         decided_by="Dr. Smith", notes="Strong alignment with our work")
    
    tracker.record_submission('TEST-001')
    
    analytics = tracker.get_analytics()
    print(f"\nAnalytics: {json.dumps(analytics, indent=2)}")
