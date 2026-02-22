"""
Collector for team data
"""

from typing import List, Set
from ..api_client import APIClient
from ..data_manager import DataManager
from ..state_manager import IngestionState
from ..utils import get_team_name_from_data


class TeamCollector:
    """
    Collects team data and last X stats
    """
    
    def __init__(self, api_client: APIClient, data_manager: DataManager, state: IngestionState):
        self.api_client = api_client
        self.data_manager = data_manager
        self.state = state
    
    def collect_league_teams(self) -> bool:
        """
        Collect all teams in the league
        
        Returns:
            True if successful, False otherwise
        """
        # Check if already complete
        if self.state.is_collection_complete('teams'):
            print("  ✓ Teams already collected")
            return True
        
        print("  Fetching teams...")
        self.state.mark_collection_in_progress('teams')
        
        all_teams = []
        page = 1
        api_calls = 0
        
        # Get already fetched team IDs
        existing_team_ids = set(self.state.get_fetched_team_ids())
        existing_from_disk = set(self.data_manager.get_all_team_ids())
        already_fetched = existing_team_ids.union(existing_from_disk)
        
        while True:
            response = self.api_client.get_league_teams(
                self.state.season_id,
                include_stats=True,
                page=page
            )
            api_calls += 1
            
            if not response or not response.get('success'):
                print(f"  ✗ Failed to fetch teams (page {page})")
                break
            
            data = response.get('data', [])
            if not data:
                break
            
            # Filter out already fetched teams
            new_teams = [team for team in data if team.get('id') not in already_fetched]
            
            # Save each team
            for team in new_teams:
                team_id = team.get('id')
                team_name = get_team_name_from_data(team)
                
                self.data_manager.save_team(team_id, team_name, team)
                all_teams.append(team)
                already_fetched.add(team_id)
                
                print(f"    ✓ Saved {team_name}")
            
            # Update state
            team_ids = [t.get('id') for t in all_teams]
            self.state.update_collection_progress(
                'teams',
                fetched=len(already_fetched),
                total=len(already_fetched),
                ids=team_ids,
                api_calls=api_calls
            )
            
            # Check if there are more pages
            pager = response.get('pager', {})
            if page >= pager.get('max_page', 1):
                break
            
            page += 1
        
        if all_teams or already_fetched:
            print(f"  ✓ Teams collected: {len(already_fetched)} total")
            self.state.mark_collection_complete('teams')
            return True
        else:
            print("  ⚠ No teams data returned")
            return False
    
    def collect_team_lastx(self) -> bool:
        """
        Collect last X stats for all teams
        
        Returns:
            True if successful, False otherwise
        """
        # Always refresh lastX stats to get latest form (even if previously complete)
        if self.state.is_collection_complete('team_lastx'):
            print("  Refreshing team lastX stats...")
        else:
            print("  Fetching lastX stats for teams...")
        
        # Get all team IDs
        team_ids = self.data_manager.get_all_team_ids()
        
        if not team_ids:
            print("  ⚠ No teams found, skipping lastX stats")
            return False
        
        self.state.mark_collection_in_progress('team_lastx')
        
        # Get already fetched from state only (not disk - we want to refresh all)
        existing = set(self.state.state['collections']['team_lastx'].get('team_ids', []))
        teams_to_fetch = team_ids  # Fetch all teams to refresh stats
        
        fetched_count = 0
        api_calls = 0
        
        for team_id in teams_to_fetch:
            # Load team to get name
            team_data = self.data_manager.load_team(team_id)
            if not team_data:
                continue
            
            team_name = get_team_name_from_data(team_data)
            
            # Fetch lastX stats
            response = self.api_client.get_team_lastx(team_id)
            api_calls += 1
            
            if response and response.get('success'):
                data = response.get('data', [])
                if data:
                    # Save all lastX variations (last 5, 6, 10)
                    self.data_manager.save_team_lastx(team_id, team_name, data)
                    fetched_count += 1
                    existing.add(team_id)
                    
                    if fetched_count % 5 == 0 or fetched_count == len(teams_to_fetch):
                        print(f"    ✓ Refreshed {fetched_count}/{len(teams_to_fetch)} teams")
            
            # Update state periodically
            if api_calls % 5 == 0:
                self.state.update_collection_progress(
                    'team_lastx',
                    fetched=fetched_count,
                    total=len(team_ids),
                    ids=list(existing),
                    api_calls=api_calls
                )
        
        # Final update
        self.state.update_collection_progress(
            'team_lastx',
            fetched=fetched_count,
            total=len(team_ids),
            ids=list(existing),
            api_calls=api_calls
        )
        
        print(f"  ✓ Team lastX stats refreshed: {fetched_count}/{len(team_ids)}")
        self.state.mark_collection_complete('team_lastx')
        return True
    
    def collect_all(self) -> bool:
        """
        Collect all team data
        
        Returns:
            True if all successful, False otherwise
        """
        print("\n👥 Collecting team data...")
        
        teams_ok = self.collect_league_teams()
        lastx_ok = self.collect_team_lastx()
        
        return teams_ok and lastx_ok