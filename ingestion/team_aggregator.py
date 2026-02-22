"""
Team data aggregator
Aggregates team data across all competitions into team-centric structure
Runs after ingestion is complete - no API calls required
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict
from datetime import datetime
from .config import LEAGUES_DIR, DATA_DIR
from .utils import get_team_name_from_data


class TeamAggregator:
    """
    Aggregates team data across all leagues/competitions
    Creates team-centric data structure
    """
    
    def __init__(self):
        self.teams_dir = DATA_DIR / "teams"
        self.teams_dir.mkdir(parents=True, exist_ok=True)
    
    def aggregate_all_teams(self) -> Dict[str, Any]:
        """
        Aggregate data for all teams across all leagues
        
        Returns:
            Summary dictionary with statistics
        """
        print("\n" + "="*60)
        print("AGGREGATING TEAM DATA ACROSS COMPETITIONS")
        print("="*60 + "\n")
        
        # Step 1: Discover all teams across all leagues
        print("📋 Step 1: Discovering teams across all leagues...")
        team_registry = self._discover_teams()
        
        print(f"   ✓ Found {len(team_registry)} unique teams\n")
        
        # Step 2: Aggregate data for each team
        print("📊 Step 2: Aggregating team data...")
        
        successful = 0
        failed = 0
        
        for idx, (team_key, team_info) in enumerate(team_registry.items(), 1):
            try:
                self._aggregate_single_team(team_key, team_info)
                successful += 1
                
                if idx % 10 == 0 or idx == len(team_registry):
                    print(f"   ✓ Processed {idx}/{len(team_registry)} teams")
            except Exception as e:
                print(f"   ✗ Failed to aggregate {team_info['name']}: {e}")
                failed += 1
        
        summary = {
            'total_teams': len(team_registry),
            'successful': successful,
            'failed': failed,
            'timestamp': datetime.now().isoformat()
        }
        
        print(f"\n{'='*60}")
        print("AGGREGATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Teams:     {summary['total_teams']}")
        print(f"Successful:      {summary['successful']}")
        print(f"Failed:          {summary['failed']}")
        print(f"{'='*60}\n")
        
        return summary
    
    def _discover_teams(self) -> Dict[str, Dict[str, Any]]:
        """
        Discover all teams across all league directories
        
        Returns:
            Dict mapping team_key to team info
        """
        team_registry = defaultdict(lambda: {
            'team_id': None,
            'name': None,
            'clean_name': None,
            'competitions': []
        })
        
        # Scan all league directories
        for league_dir in LEAGUES_DIR.iterdir():
            if not league_dir.is_dir():
                continue
            
            # Extract league_key and season_id from directory name
            dir_name = league_dir.name
            parts = dir_name.rsplit('_', 1)
            if len(parts) != 2:
                continue
            
            league_key = parts[0]
            try:
                season_id = int(parts[1])
            except ValueError:
                continue
            
            # Load league table to get teams
            table_file = league_dir / "league_table.json"
            if not table_file.exists():
                continue
            
            try:
                with open(table_file, 'r') as f:
                    table_data = json.load(f)
                
                teams = self._extract_teams_from_table(table_data)
                
                # Register each team
                for team in teams:
                    team_id = team.get('id')
                    team_name = team.get('name', team.get('cleanName', ''))
                    clean_name = self._sanitize_team_name(team_name)
                    
                    if not clean_name or not team_id:
                        continue
                    
                    # Use team_id as primary key (more reliable than name)
                    team_key = str(team_id)
                    
                    # Update team info
                    if team_registry[team_key]['team_id'] is None:
                        team_registry[team_key]['team_id'] = team_id
                        team_registry[team_key]['name'] = team_name
                        team_registry[team_key]['clean_name'] = clean_name
                    
                    # Add competition
                    team_registry[team_key]['competitions'].append({
                        'league_key': league_key,
                        'season_id': season_id,
                        'league_dir': str(league_dir)
                    })
            
            except Exception as e:
                print(f"   ⚠ Error processing {league_dir.name}: {e}")
                continue
        
        return dict(team_registry)
    
    def _extract_teams_from_table(self, table_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract team list from league table data"""
        teams = []
        
        # Handle the data wrapper
        if 'data' in table_data:
            actual_data = table_data['data']
        else:
            actual_data = table_data
        
        # Handle different table structures
        if isinstance(actual_data, list):
            # Direct list of teams
            teams = actual_data
        elif isinstance(actual_data, dict):
            # Check for specific_tables
            specific_tables = actual_data.get('specific_tables', [])
            
            for round_data in specific_tables:
                # Single table format
                if round_data.get('table'):
                    teams.extend(round_data['table'])
                
                # Group format (tournaments)
                elif round_data.get('groups'):
                    for group in round_data['groups']:
                        if group.get('table'):
                            teams.extend(group['table'])
        
        # Deduplicate by team ID
        unique_teams = {}
        for team in teams:
            team_id = team.get('id')
            if team_id and team_id not in unique_teams:
                unique_teams[team_id] = team
        
        return list(unique_teams.values())
    
    def _aggregate_single_team(self, team_key: str, team_info: Dict[str, Any]):
        """
        Aggregate data for a single team across all competitions
        
        Args:
            team_key: Unique team identifier
            team_info: Team information including competitions
        """
        team_id = team_info['team_id']
        team_name = team_info['name']
        clean_name = team_info['clean_name']
        competitions = team_info['competitions']
        
        # Create team directory
        team_dir = self.teams_dir / clean_name
        team_dir.mkdir(parents=True, exist_ok=True)
        
        # Save basic team info
        team_master_info = {
            'team_id': team_id,
            'name': team_name,
            'clean_name': clean_name,
            'competitions': [
                {
                    'league_key': c['league_key'],
                    'season_id': c['season_id']
                }
                for c in competitions
            ],
            'last_updated': datetime.now().isoformat()
        }
        
        with open(team_dir / "team_info.json", 'w') as f:
            json.dump(team_master_info, f, indent=2)
        
        # Aggregate fixtures and stats
        all_fixtures = []
        all_stats = {}
        
        for comp in competitions:
            league_dir = Path(comp['league_dir'])
            
            # Load matches
            matches_dir = league_dir / "matches"
            if matches_dir.exists():
                team_matches = []
                for match_file in matches_dir.glob("*.json"):
                    try:
                        with open(match_file, 'r') as f:
                            match = json.load(f)
                        
                        # Check if team is involved
                        if match.get('homeID') == team_id or match.get('awayID') == team_id:
                            # Add competition context
                            match['_league_key'] = comp['league_key']
                            match['_season_id'] = comp['season_id']
                            team_matches.append(match)
                    except Exception:
                        continue
                
                all_fixtures.extend(team_matches)
            
            # Load team stats from league table
            table_file = league_dir / "league_table.json"
            if table_file.exists():
                try:
                    with open(table_file, 'r') as f:
                        table_data = json.load(f)
                    
                    teams = self._extract_teams_from_table(table_data)
                    team_stats = next((t for t in teams if t.get('id') == team_id), None)
                    
                    if team_stats:
                        all_stats[comp['league_key']] = team_stats
                except Exception:
                    pass
        
        # Sort fixtures by date
        all_fixtures.sort(key=lambda x: x.get('date_unix', 0))
        
        # Save all fixtures
        with open(team_dir / "all_fixtures.json", 'w') as f:
            json.dump({
                'team_id': team_id,
                'team_name': team_name,
                'total_fixtures': len(all_fixtures),
                'fixtures': all_fixtures,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
        
        # Calculate aggregated stats
        aggregated = self._calculate_aggregated_stats(all_stats, all_fixtures, team_id)
        
        # Save aggregated stats
        with open(team_dir / "all_stats.json", 'w') as f:
            json.dump({
                'team_id': team_id,
                'team_name': team_name,
                'aggregated_stats': aggregated,
                'by_competition': all_stats,
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    
    def _calculate_aggregated_stats(self, competition_stats: Dict[str, Any], 
                                   fixtures: List[Dict[str, Any]], 
                                   team_id: int) -> Dict[str, Any]:
        """Calculate aggregated statistics across all competitions"""
        
        # Filter to completed matches only
        completed = [f for f in fixtures if f.get('status') == 'complete']
        
        if not completed:
            return {
                'matches_played': 0,
                'wins': 0,
                'draws': 0,
                'losses': 0,
                'goals_scored': 0,
                'goals_conceded': 0
            }
        
        # Calculate from fixtures
        wins = 0
        draws = 0
        losses = 0
        goals_scored = 0
        goals_conceded = 0
        clean_sheets = 0
        btts_count = 0
        over25_count = 0
        
        for fixture in completed:
            home_id = fixture.get('homeID')
            away_id = fixture.get('awayID')
            home_goals = fixture.get('homeGoalCount', 0)
            away_goals = fixture.get('awayGoalCount', 0)
            
            # Determine if home or away
            if home_id == team_id:
                team_goals = home_goals
                opponent_goals = away_goals
            else:
                team_goals = away_goals
                opponent_goals = home_goals
            
            goals_scored += team_goals
            goals_conceded += opponent_goals
            
            # Win/draw/loss
            if team_goals > opponent_goals:
                wins += 1
            elif team_goals == opponent_goals:
                draws += 1
            else:
                losses += 1
            
            # Clean sheet
            if opponent_goals == 0:
                clean_sheets += 1
            
            # BTTS
            if home_goals > 0 and away_goals > 0:
                btts_count += 1
            
            # Over 2.5
            if (home_goals + away_goals) > 2.5:
                over25_count += 1
        
        matches = len(completed)
        
        return {
            'matches_played': matches,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'clean_sheets': clean_sheets,
            'win_percentage': round((wins / matches) * 100, 2) if matches > 0 else 0,
            'draw_percentage': round((draws / matches) * 100, 2) if matches > 0 else 0,
            'loss_percentage': round((losses / matches) * 100, 2) if matches > 0 else 0,
            'goals_per_game': round(goals_scored / matches, 2) if matches > 0 else 0,
            'goals_conceded_per_game': round(goals_conceded / matches, 2) if matches > 0 else 0,
            'clean_sheet_percentage': round((clean_sheets / matches) * 100, 2) if matches > 0 else 0,
            'btts_percentage': round((btts_count / matches) * 100, 2) if matches > 0 else 0,
            'over25_percentage': round((over25_count / matches) * 100, 2) if matches > 0 else 0
        }
    
    def _sanitize_team_name(self, name: str) -> str:
        """Sanitize team name for use as directory name"""
        # Replace spaces with underscores
        name = name.replace(' ', '_')
        
        # Remove special characters
        safe_chars = []
        for char in name:
            if char.isalnum() or char in ['_', '-']:
                safe_chars.append(char)
        
        result = ''.join(safe_chars).lower()
        
        # Limit length
        return result[:50]


def aggregate_teams() -> Dict[str, Any]:
    """
    Convenience function to run team aggregation
    
    Returns:
        Summary dictionary
    """
    aggregator = TeamAggregator()
    return aggregator.aggregate_all_teams()