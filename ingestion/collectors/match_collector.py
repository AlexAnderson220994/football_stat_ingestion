"""
Collector for match data
"""

from typing import List, Set
from ..api_client import APIClient
from ..data_manager import DataManager
from ..state_manager import IngestionState


class MatchCollector:
    """
    Collects match data
    """
    
    def __init__(self, api_client: APIClient, data_manager: DataManager, state: IngestionState):
        self.api_client = api_client
        self.data_manager = data_manager
        self.state = state
    
    def collect_league_matches(self) -> bool:
        """
        Collect all matches in the league
        
        Returns:
            True if successful, False otherwise
        """
        # Always check for new matches and update existing ones (even if previously complete)
        if self.state.is_collection_complete('matches'):
            print("  Checking for new matches and updating existing...")
        else:
            print("  Fetching matches...")
        
        self.state.mark_collection_in_progress('matches')
        
        all_match_ids = set()
        page = 1
        api_calls = 0
        new_count = 0
        updated_count = 0
        
        # Get already fetched match IDs from disk
        existing_from_disk = set(self.data_manager.get_all_match_ids())
        
        while True:
            response = self.api_client.get_league_matches(
                self.state.season_id,
                page=page,
                max_per_page=500
            )
            api_calls += 1
            
            if not response or not response.get('success'):
                print(f"  ✗ Failed to fetch matches (page {page})")
                break
            
            data = response.get('data', [])
            if not data:
                break
            
            # Save ALL matches (new and existing) to capture status updates
            for match in data:
                match_id = match.get('id')
                
                # Determine if this is new or an update
                if match_id in existing_from_disk:
                    updated_count += 1
                else:
                    new_count += 1
                
                # Always save to capture any updates (especially status changes)
                self.data_manager.save_match(match_id, match)
                all_match_ids.add(match_id)
            
            # Progress update
            if data:
                print(f"    ✓ Page {page}: {len(data)} matches processed")
            
            # Update state
            self.state.update_collection_progress(
                'matches',
                fetched=len(all_match_ids.union(existing_from_disk)),
                total=len(all_match_ids.union(existing_from_disk)),
                ids=list(all_match_ids),
                api_calls=api_calls
            )
            
            # Check if there are more pages
            pager = response.get('pager', {})
            if page >= pager.get('max_page', 1):
                break
            
            page += 1
        
        total_matches = len(all_match_ids.union(existing_from_disk))
        
        if new_count > 0 or updated_count > 0:
            print(f"  ✓ Matches: {total_matches} total ({new_count} new, {updated_count} updated)")
            self.state.mark_collection_complete('matches')
            return True
        elif total_matches > 0:
            print(f"  ✓ Matches: {total_matches} total (no changes)")
            self.state.mark_collection_complete('matches')
            return True
        else:
            print("  ⚠ No matches data returned")
            return False
    
    def collect_all(self) -> bool:
        """
        Collect all match data
        
        Returns:
            True if successful, False otherwise
        """
        print("\n⚽ Collecting match data...")
        
        return self.collect_league_matches()