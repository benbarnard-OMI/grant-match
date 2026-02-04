"""
FastAPI-based REST API for MPART grant system.

Provides endpoints for:
- Retrieving grant matches
- Managing decisions
- Exporting data
- Webhook integrations
"""

import os
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from functools import wraps

# FastAPI imports
try:
    from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
    from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


logger = logging.getLogger(__name__)

# Ensure src/ is on the path when running as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


if FASTAPI_AVAILABLE:
    
    # Pydantic models
    class MatchResponse(BaseModel):
        grant_id: str
        grant_title: str
        match_score: int
        recommended_lead: str
        deadline: Optional[str]
        rationale: str
        
    class DecisionUpdate(BaseModel):
        status: str
        decided_by: Optional[str] = None
        notes: Optional[str] = None
    
    class ExportRequest(BaseModel):
        format: str = "json"  # json, csv, excel
        min_score: int = 0
        status_filter: Optional[List[str]] = None
    
    
    def create_api() -> FastAPI:
        """Create and configure the FastAPI application."""
        
        app = FastAPI(
            title="MPART @ UIS Grant Match API",
            description="API for accessing grant matches and managing decisions",
            version="2.0.0"
        )
        
        # CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Load data
        def load_matches() -> Dict:
            """Load current matches."""
            matches_file = Path("data/mpart_matches.json")
            if not matches_file.exists():
                return {"matches": [], "metadata": {}}
            
            with open(matches_file) as f:
                return json.load(f)
        
        def load_decisions() -> Dict:
            """Load decisions."""
            decisions_file = Path("data/grant_decisions.json")
            if not decisions_file.exists():
                return {"decisions": []}
            
            with open(decisions_file) as f:
                return json.load(f)
        
        # Routes
        @app.get("/")
        async def root():
            """API root with basic info."""
            return {
                "name": "MPART @ UIS Grant Match API",
                "version": "2.0.0",
                "status": "operational",
                "endpoints": [
                    "/matches",
                    "/matches/{grant_id}",
                    "/decisions",
                    "/decisions/{grant_id}",
                    "/analytics",
                    "/export"
                ]
            }
        
        @app.get("/matches", response_model=List[MatchResponse])
        async def get_matches(
            min_score: int = Query(0, ge=0, le=100),
            lead: Optional[str] = Query(None),
            status: Optional[str] = Query(None),
            limit: int = Query(100, ge=1, le=1000)
        ):
            """
            Get grant matches with optional filtering.
            
            Args:
                min_score: Minimum match score (0-100)
                lead: Filter by assigned lead
                status: Filter by status
                limit: Maximum number of results
            """
            data = load_matches()
            matches = data.get('matches', [])
            
            # Apply filters
            filtered = matches
            
            if min_score > 0:
                filtered = [m for m in filtered if m.get('match_score', 0) >= min_score]
            
            if lead:
                filtered = [m for m in filtered if lead.lower() in m.get('recommended_lead', '').lower()]
            
            if status:
                # Check if there's a decision with this status
                decisions_data = load_decisions()
                decision_map = {d['grant_id']: d for d in decisions_data.get('decisions', [])}
                filtered = [m for m in filtered if decision_map.get(m['grant_id'], {}).get('status') == status]
            
            return filtered[:limit]
        
        @app.get("/matches/{grant_id}")
        async def get_match(grant_id: str):
            """Get a specific match by ID."""
            data = load_matches()
            
            for match in data.get('matches', []):
                if match.get('grant_id') == grant_id:
                    # Include decision info if available
                    decisions_data = load_decisions()
                    decision = next(
                        (d for d in decisions_data.get('decisions', []) if d['grant_id'] == grant_id),
                        None
                    )
                    
                    return {
                        "match": match,
                        "decision": decision
                    }
            
            raise HTTPException(status_code=404, detail="Grant not found")
        
        @app.get("/decisions")
        async def get_decisions(
            status: Optional[str] = Query(None),
            lead: Optional[str] = Query(None)
        ):
            """Get all tracked decisions."""
            data = load_decisions()
            decisions = data.get('decisions', [])
            
            if status:
                decisions = [d for d in decisions if d.get('status') == status]
            
            if lead:
                decisions = [d for d in decisions if lead.lower() in d.get('assigned_lead', '').lower()]
            
            return {"decisions": decisions}
        
        @app.post("/decisions/{grant_id}")
        async def update_decision(grant_id: str, update: DecisionUpdate):
            """Update the decision status for a grant."""
            # This would integrate with DecisionTracker
            from tracking import DecisionTracker, DecisionStatus
            
            tracker = DecisionTracker()
            
            try:
                status = DecisionStatus(update.status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {update.status}")
            
            decision = tracker.update_status(
                grant_id=grant_id,
                status=status,
                decided_by=update.decided_by or "API",
                notes=update.notes
            )
            
            if not decision:
                raise HTTPException(status_code=404, detail="Grant not found")
            
            return {"success": True, "decision": decision.to_dict()}
        
        @app.get("/analytics")
        async def get_analytics():
            """Get analytics and statistics."""
            from tracking import DecisionTracker
            
            tracker = DecisionTracker()
            analytics = tracker.get_analytics()
            
            # Add match analytics
            data = load_matches()
            matches = data.get('matches', [])
            
            score_distribution = {"90-100": 0, "80-89": 0, "70-79": 0, "60-69": 0, "50-59": 0, "<50": 0}
            for m in matches:
                score = m.get('match_score', 0)
                if score >= 90:
                    score_distribution["90-100"] += 1
                elif score >= 80:
                    score_distribution["80-89"] += 1
                elif score >= 70:
                    score_distribution["70-79"] += 1
                elif score >= 60:
                    score_distribution["60-69"] += 1
                elif score >= 50:
                    score_distribution["50-59"] += 1
                else:
                    score_distribution["<50"] += 1
            
            return {
                "decisions": analytics,
                "matches": {
                    "total": len(matches),
                    "score_distribution": score_distribution
                }
            }
        
        @app.post("/export")
        async def export_data(request: ExportRequest):
            """Export matches in various formats."""
            data = load_matches()
            matches = data.get('matches', [])
            
            # Filter
            matches = [m for m in matches if m.get('match_score', 0) >= request.min_score]
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if request.format == 'json':
                return JSONResponse(content={"matches": matches})
            
            elif request.format == 'csv':
                from export import CSVExporter
                exporter = CSVExporter()
                filepath = exporter.export(matches, f"data/export_{timestamp}.csv")
                return FileResponse(filepath, filename=f"mpart_matches_{timestamp}.csv")
            
            elif request.format == 'excel':
                from export import ExcelExporter
                exporter = ExcelExporter()
                filepath = exporter.export(matches, f"data/export_{timestamp}.xlsx")
                return FileResponse(filepath, filename=f"mpart_matches_{timestamp}.xlsx")
            
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
        
        @app.get("/calendar/deadlines.ics")
        async def get_calendar():
            """Get calendar file with all deadlines."""
            from integrations import CalendarIntegration
            
            calendar = CalendarIntegration()
            decisions_data = load_decisions()
            
            filepath = calendar.generate_ics(decisions_data.get('decisions', []))
            
            return FileResponse(
                filepath,
                filename="mpart_deadlines.ics",
                media_type="text/calendar"
            )
        
        @app.post("/webhook/refresh")
        async def trigger_refresh(background_tasks: BackgroundTasks):
            """Trigger a refresh of grant data."""
            def run_discovery():
                # This would run the actual discovery
                logger.info("Discovery triggered via webhook")
            
            background_tasks.add_task(run_discovery)
            
            return {"success": True, "message": "Discovery triggered in background"}
        
        return app

else:
    # FastAPI not available - provide stub
    def create_api():
        """Stub when FastAPI is not installed."""
        logger.error("FastAPI not installed. Run: pip install fastapi uvicorn")
        raise ImportError("FastAPI required. Install: pip install fastapi uvicorn")


if __name__ == '__main__':
    if FASTAPI_AVAILABLE:
        import uvicorn
        
        app = create_api()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        print("FastAPI not available. Install with: pip install fastapi uvicorn")
