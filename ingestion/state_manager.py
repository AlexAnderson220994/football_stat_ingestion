"""
State manager for tracking ingestion progress
Allows resuming interrupted ingestions
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
from .config import STATE_DIR


class IngestionState:
    """
    Manages state for a single league/season ingestion
    Tracks progress and allows resuming
    """
    
    def __init__(self, league_key: str, season_id: int, season_year: str):
        self.league_key = league_key
        self.season_id = season_id
        self.season_year = season_year
        self.state_file = STATE_DIR / f"{league_key}_{season_id}_state.json"
        
        # Initialize or load state
        self.state = self._load_or_initialize()
    
    def _load_or_initialize(self) -> Dict:
        """Load existing state or create new one"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠ Could not load state file: {e}")
                return self._create_initial_state()
        else:
            return self._create_initial_state()
    
    def _create_initial_state(self) -> Dict:
        """Create initial state structure"""
        return {
            'league': self.league_key,
            'season_id': self.season_id,
            'season_year': self.season_year,
            'started_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'status': 'not_started',  # not_started, in_progress, complete
            'collections': {
                'league_stats': {
                    'status': 'pending',
                    'last_updated': None,
                    'api_calls': 0
                },
                'league_table': {
                    'status': 'pending',
                    'last_updated': None,
                    'api_calls': 0
                },
                'teams': {
                    'status': 'pending',
                    'total': 0,
                    'fetched': 0,
                    'team_ids': [],
                    'api_calls': 0
                },
                'team_lastx': {
                    'status': 'pending',
                    'total': 0,
                    'fetched': 0,
                    'team_ids': [],
                    'api_calls': 0
                },
                'matches': {
                    'status': 'pending',
                    'total': 0,
                    'fetched': 0,
                    'match_ids': [],
                    'api_calls': 0
                },
                'match_details': {
                    'status': 'pending',
                    'total': 0,
                    'fetched': 0,
                    'match_ids': [],
                    'api_calls': 0
                },
                'players': {
                    'status': 'pending',
                    'total': 0,
                    'fetched': 0,
                    'player_ids': [],
                    'api_calls': 0
                },
                'referees': {
                    'status': 'pending',
                    'total': 0,
                    'fetched': 0,
                    'referee_ids': [],
                    'api_calls': 0
                },
                'h2h': {
                    'status': 'pending',
                    'generated': 0,
                    'last_updated': None
                }
            },
            'total_api_calls': 0,
            'estimated_remaining_calls': 0
        }
    
    def save(self):
        """Save current state to disk"""
        self.state['last_updated'] = datetime.now().isoformat()
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"✗ Could not save state: {e}")
    
    def mark_collection_complete(self, collection: str):
        """Mark a collection as complete"""
        if collection in self.state['collections']:
            self.state['collections'][collection]['status'] = 'complete'
            self.state['collections'][collection]['last_updated'] = datetime.now().isoformat()
            self.save()
    
    def mark_collection_in_progress(self, collection: str):
        """Mark a collection as in progress"""
        if collection in self.state['collections']:
            self.state['collections'][collection]['status'] = 'in_progress'
            self.save()
    
    def update_collection_progress(self, collection: str, fetched: int, total: Optional[int] = None, 
                                   ids: Optional[List] = None, api_calls: int = 0):
        """Update progress for a collection"""
        if collection in self.state['collections']:
            coll_state = self.state['collections'][collection]
            coll_state['fetched'] = fetched
            
            if total is not None:
                coll_state['total'] = total
            
            if ids is not None:
                # Merge new IDs with existing ones
                if 'team_ids' in coll_state:
                    existing = set(coll_state['team_ids'])
                    existing.update(ids)
                    coll_state['team_ids'] = sorted(list(existing))
                elif 'match_ids' in coll_state:
                    existing = set(coll_state['match_ids'])
                    existing.update(ids)
                    coll_state['match_ids'] = sorted(list(existing))
                elif 'player_ids' in coll_state:
                    existing = set(coll_state['player_ids'])
                    existing.update(ids)
                    coll_state['player_ids'] = sorted(list(existing))
                elif 'referee_ids' in coll_state:
                    existing = set(coll_state['referee_ids'])
                    existing.update(ids)
                    coll_state['referee_ids'] = sorted(list(existing))
            
            if api_calls > 0:
                coll_state['api_calls'] = coll_state.get('api_calls', 0) + api_calls
                self.state['total_api_calls'] = self.state.get('total_api_calls', 0) + api_calls
            
            self.save()
    
    def get_fetched_team_ids(self) -> List[int]:
        """Get list of already fetched team IDs"""
        return self.state['collections']['teams'].get('team_ids', [])
    
    def get_fetched_match_ids(self) -> List[int]:
        """Get list of already fetched match IDs"""
        return self.state['collections']['matches'].get('match_ids', [])
    
    def get_fetched_player_ids(self) -> List[int]:
        """Get list of already fetched player IDs"""
        return self.state['collections']['players'].get('player_ids', [])
    
    def get_fetched_referee_ids(self) -> List[int]:
        """Get list of already fetched referee IDs"""
        return self.state['collections']['referees'].get('referee_ids', [])
    
    def is_collection_complete(self, collection: str) -> bool:
        """Check if a collection is complete"""
        if collection not in self.state['collections']:
            return False
        return self.state['collections'][collection].get('status') == 'complete'
    
    def get_overall_status(self) -> str:
        """
        Get overall ingestion status
        
        Returns:
            'complete', 'in_progress', or 'not_started'
        """
        collections = self.state['collections']
        
        # Check if all collections are complete
        all_complete = all(
            coll.get('status') == 'complete' 
            for coll in collections.values()
        )
        
        if all_complete:
            return 'complete'
        
        # Check if any collection is in progress or complete
        any_started = any(
            coll.get('status') in ['in_progress', 'complete']
            for coll in collections.values()
        )
        
        if any_started:
            return 'in_progress'
        
        return 'not_started'
    
    def mark_complete(self):
        """Mark entire ingestion as complete"""
        self.state['status'] = 'complete'
        self.state['completed_at'] = datetime.now().isoformat()
        self.save()
    
    def get_summary(self) -> Dict:
        """Get summary of ingestion state"""
        collections = self.state['collections']
        
        return {
            'league': self.league_key,
            'season_id': self.season_id,
            'season_year': self.season_year,
            'status': self.get_overall_status(),
            'started_at': self.state.get('started_at'),
            'last_updated': self.state.get('last_updated'),
            'total_api_calls': self.state.get('total_api_calls', 0),
            'collections': {
                name: {
                    'status': coll.get('status'),
                    'progress': f"{coll.get('fetched', 0)}/{coll.get('total', 0)}" 
                               if 'fetched' in coll else None
                }
                for name, coll in collections.items()
            }
        }


def get_all_ingestion_states() -> Dict[str, IngestionState]:
    """
    Get all existing ingestion states
    
    Returns:
        Dict mapping league_season keys to IngestionState objects
    """
    states = {}
    
    for state_file in STATE_DIR.glob("*_state.json"):
        try:
            with open(state_file, 'r') as f:
                state_data = json.load(f)
                league_key = state_data.get('league')
                season_id = state_data.get('season_id')
                
                if league_key and season_id:
                    key = f"{league_key}_{season_id}"
                    # Create a state object and set its data
                    state_obj = IngestionState(
                        league_key,
                        season_id,
                        state_data.get('season_year', '')
                    )
                    state_obj.state = state_data
                    states[key] = state_obj
        except Exception as e:
            print(f"⚠ Could not load state file {state_file}: {e}")
            continue
    
    return states