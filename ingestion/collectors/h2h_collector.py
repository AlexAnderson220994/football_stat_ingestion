"""
Collector for head-to-head data
Generates H2H stats from match data (no API calls needed)
"""

from typing import List, Dict
from itertools import combinations
from ..data_manager import DataManager
from ..state_manager import IngestionState
from ..utils import calculate_h2h_stats


class H2HCollector:
    """
    Generates head-to-head statistics from match data
    """
    
    def __init__(self, data_manager: DataManager, state: IngestionState):
        self.data_manager = data_manager
        self.state = state
    
    def collect_h2h_data(self) -> bool:
        """
        Generate H2H data for all team pairs
        
        Returns:
            True if successful, False otherwise
        """
        # Always regenerate H2H from updated match data (even if previously complete)
        if self.state.is_collection_complete('h2h'):
            print("  Regenerating H2H data from updated matches...")
        else:
            print("  Generating H2H data from matches...")
        
        self.state.mark_collection_in_progress('h2h')
        
        # Get all teams
        team_ids = self.data_manager.get_all_team_ids()
        
        if len(team_ids) < 2:
            print("  ⚠ Not enough teams for H2H generation")
            return False
        
        # Get all matches
        match_ids = self.data_manager.get_all_match_ids()
        all_matches = []
        
        for match_id in match_ids:
            match = self.data_manager.load_match(match_id)
            if match:
                all_matches.append(match)
        
        if not all_matches:
            print("  ⚠ No matches found for H2H generation")
            return False
        
        # Generate H2H for each team pair
        h2h_count = 0
        team_pairs = list(combinations(team_ids, 2))
        
        print(f"  Processing {len(team_pairs)} team pairs...")
        
        for team_a_id, team_b_id in team_pairs:
            # Find matches between these two teams
            h2h_matches = [
                match for match in all_matches
                if (match.get('homeID') == team_a_id and match.get('awayID') == team_b_id) or
                   (match.get('homeID') == team_b_id and match.get('awayID') == team_a_id)
            ]
            
            if h2h_matches:
                # Calculate H2H stats
                h2h_stats = calculate_h2h_stats(h2h_matches, team_a_id, team_b_id)
                
                # Add metadata
                h2h_data = {
                    'team_a_id': team_a_id,
                    'team_b_id': team_b_id,
                    'matches': h2h_matches,
                    'stats': h2h_stats
                }
                
                # Save H2H data (overwrites existing to include new matches)
                self.data_manager.save_h2h(team_a_id, team_b_id, h2h_data)
                h2h_count += 1
        
        # Update state
        self.state.state['collections']['h2h']['generated'] = h2h_count
        self.state.state['collections']['h2h']['last_updated'] = self.state.state['last_updated']
        self.state.mark_collection_complete('h2h')
        
        print(f"  ✓ H2H data generated: {h2h_count} team pairs")
        return True
    
    def collect_all(self) -> bool:
        """
        Collect all H2H data
        
        Returns:
            True if successful, False otherwise
        """
        print("\n🤝 Generating H2H data...")
        
        return self.collect_h2h_data()