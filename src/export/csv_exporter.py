"""
CSV export functionality for grant matches.
"""

import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)


class CSVExporter:
    """Export grant matches to CSV format."""
    
    def __init__(self, delimiter: str = ',', include_headers: bool = True):
        self.delimiter = delimiter
        self.include_headers = include_headers
    
    def export(self, matches: List[Dict], 
               output_path: Optional[str] = None) -> str:
        """
        Export matches to CSV file.
        
        Args:
            matches: List of match dictionaries
            output_path: Path for output file
            
        Returns:
            Path to exported file
        """
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"data/mpart_matches_{timestamp}.csv"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Flatten data for CSV
        flattened = self._flatten_matches(matches)
        
        if not flattened:
            logger.warning("No data to export")
            return str(output_path)
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=flattened[0].keys(), 
                                   delimiter=self.delimiter)
            
            if self.include_headers:
                writer.writeheader()
            
            writer.writerows(flattened)
        
        logger.info(f"CSV exported to {output_path}")
        return str(output_path)
    
    def _flatten_matches(self, matches: List[Dict]) -> List[Dict]:
        """Flatten nested match data for CSV export."""
        flattened = []
        
        for match in matches:
            flat = {
                'grant_id': match.get('grant_id', ''),
                'grant_title': match.get('grant_title', ''),
                'agency': match.get('agency', ''),
                'match_score': match.get('match_score', 0),
                'keyword_score': match.get('keyword_score', 0),
                'priority': 'High' if match.get('match_score', 0) >= 80 else 
                           'Medium' if match.get('match_score', 0) >= 50 else 'Low',
                'deadline': match.get('deadline', ''),
                'research_depth': match.get('research_depth', ''),
                'recommended_lead': match.get('recommended_lead', ''),
                'lead_display': self._format_lead(match.get('recommended_lead', '')),
                'rationale': match.get('rationale', ''),
                'recommended_action': match.get('recommended_action', ''),
                'timestamp': match.get('timestamp', ''),
                'alignment_points': '; '.join(match.get('alignment_points', []))
            }
            flattened.append(flat)
        
        return flattened
    
    def _format_lead(self, lead_id: str) -> str:
        """Format lead ID for display."""
        mapping = {
            'mercenary_policy': 'Policy Expert',
            'mercenary_data': 'Data/AI Expert',
            'mercenary_eval': 'Rural/Eval Expert',
            '': 'Unassigned'
        }
        return mapping.get(lead_id, lead_id)


def export_matches_to_csv(matches_file: str = "data/mpart_matches.json",
                         output_file: Optional[str] = None) -> str:
    """Convenience function to export matches to CSV."""
    with open(matches_file) as f:
        data = json.load(f)
    
    matches = data.get('matches', [])
    
    exporter = CSVExporter()
    return exporter.export(matches, output_file)


if __name__ == '__main__':
    try:
        output = export_matches_to_csv()
        print(f"✓ CSV exported to: {output}")
    except FileNotFoundError:
        print("❌ No matches file found.")
