"""
Collector for detailed match data
Fetches in-depth match statistics for completed matches only
"""

from typing import List, Set
from ..api_client import APIClient
from ..data_manager import DataManager
from ..state_manager import IngestionState


class MatchDetailsCollector:
    """
    Collects detailed match statistics for completed matches
    """
    
    def __init__(self, api_client: APIClient, data_manager: DataManager, state: IngestionState):
        self.api_client = api_client
        self.data_manager = data_manager
        self.state = state
    
    def collect_match_details(self) -> bool:
        """
        Collect detailed match data for all completed matches
        
        Returns:
            True if successful, False otherwise
        """
        # Always check for new match details (even if previously complete)
        if self.state.is_collection_complete('match_details'):
            print("  Checking for new match details...")
        else:
            print("  Fetching match details for completed matches...")
        
        self.state.mark_collection_in_progress('match_details')
        
        # Get all match IDs
        all_match_ids = self.data_manager.get_all_match_ids()
        
        if not all_match_ids:
            print("  ⚠ No matches found")
            return False
        
        # Filter to completed matches only
        completed_match_ids = []
        for match_id in all_match_ids:
            match = self.data_manager.load_match(match_id)
            if match and match.get('status') == 'complete':
                completed_match_ids.append(match_id)
        
        if not completed_match_ids:
            print("  ℹ No completed matches to collect details for")
            self.state.mark_collection_complete('match_details')
            return True
        
        # Get already fetched details
        existing = set(self.state.state['collections'].get('match_details', {}).get('match_ids', []))
        existing_from_disk = set(self.data_manager.get_all_match_detail_ids())
        already_fetched = existing.union(existing_from_disk)
        
        # Find new matches to collect
        matches_to_fetch = [mid for mid in completed_match_ids if mid not in already_fetched]
        
        if not matches_to_fetch:
            print(f"  ✓ All {len(completed_match_ids)} completed matches already have details")
            self.state.mark_collection_complete('match_details')
            return True
        
        print(f"  Found {len(completed_match_ids)} completed matches")
        print(f"  Already collected: {len(already_fetched)}")
        print(f"  New to collect: {len(matches_to_fetch)}")
        
        fetched_count = len(already_fetched)
        api_calls = 0
        
        for idx, match_id in enumerate(matches_to_fetch, 1):
            # Load basic match data for display
            match = self.data_manager.load_match(match_id)
            if not match:
                continue
            
            home_name = match.get('home_name', 'Unknown')
            away_name = match.get('away_name', 'Unknown')
            
            # Fetch detailed match data
            response = self.api_client.get_match(match_id)
            api_calls += 1
            
            if response and response.get('success'):
                data = response.get('data', {})
                if data:
                    # Save match details
                    self.data_manager.save_match_details(match_id, data)
                    fetched_count += 1
                    already_fetched.add(match_id)
                    
                    if idx % 10 == 0 or idx == len(matches_to_fetch):
                        print(f"    ✓ {idx}/{len(matches_to_fetch)} match details collected")
            
            # Update state periodically
            if api_calls % 10 == 0:
                self.state.update_collection_progress(
                    'match_details',
                    fetched=fetched_count,
                    total=len(completed_match_ids),
                    ids=list(already_fetched),
                    api_calls=api_calls
                )
        
        # Final update
        self.state.update_collection_progress(
            'match_details',
            fetched=fetched_count,
            total=len(completed_match_ids),
            ids=list(already_fetched),
            api_calls=api_calls
        )
        
        print(f"  ✓ Match details collected: {fetched_count}/{len(completed_match_ids)}")
        self.state.mark_collection_complete('match_details')
        return True
    
    def collect_all(self) -> bool:
        """
        Collect all match details
        
        Returns:
            True if successful, False otherwise
        """
        print("\n📋 Collecting match details...")
        
        return self.collect_match_details()