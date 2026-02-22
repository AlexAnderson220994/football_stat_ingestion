"""
Interactive league and season selector
"""

from typing import Optional, Dict, Tuple
from .config import TARGET_LEAGUES
from .league_mapper import LeagueMapper
from .state_manager import get_all_ingestion_states
from rich.console import Console
from rich.table import Table

console = Console()


class LeagueSelector:
    """
    Interactive selector for leagues and seasons
    """
    
    def __init__(self, league_mapper: LeagueMapper):
        self.league_mapper = league_mapper
        self.leagues_data = None
    
    def show_league_menu(self) -> Optional[Tuple[str, str, Dict]]:
        """
        Show interactive league selection menu
        
        Returns:
            Tuple of (league_key, league_name, league_data) or None if cancelled
        """
        # Fetch leagues if not already loaded
        if not self.leagues_data:
            console.print("\n[yellow]Loading league data...[/yellow]")
            self.leagues_data = self.league_mapper.fetch_and_map_leagues()
        
        # Get ingestion states for status display
        states = get_all_ingestion_states()
        
        # Create table
        table = Table(title="Available Leagues", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("League", style="cyan")
        table.add_column("Country", style="green")
        table.add_column("Current Season", style="yellow")
        table.add_column("Last Season", style="yellow")
        
        league_list = []
        for idx, (key, league) in enumerate(self.leagues_data.items(), 1):
            league_list.append((key, league))
            
            # Get status for current season
            latest_season = self.league_mapper.get_latest_season(key)
            second_latest = self.league_mapper.get_second_latest_season(key)
            
            current_status = "✗ Not started"
            last_status = "✗ Not started"
            
            if latest_season:
                state_key = f"{key}_{latest_season['id']}"
                if state_key in states:
                    status = states[state_key].get_overall_status()
                    if status == 'complete':
                        current_status = "✓ Complete"
                    elif status == 'in_progress':
                        current_status = "⚠ Partial"
            
            if second_latest:
                state_key = f"{key}_{second_latest['id']}"
                if state_key in states:
                    status = states[state_key].get_overall_status()
                    if status == 'complete':
                        last_status = "✓ Complete"
                    elif status == 'in_progress':
                        last_status = "⚠ Partial"
            
            table.add_row(
                str(idx),
                league['name'],
                league['country'],
                current_status,
                last_status
            )
        
        console.print("\n")
        console.print(table)
        console.print("\n[dim]Legend:[/dim]")
        console.print("[dim]  ✓ Complete = All data ingested for this season[/dim]")
        console.print("[dim]  ⚠ Partial = Some data missing (interrupted/in-progress)[/dim]")
        console.print("[dim]  ✗ Not started = No data ingested yet[/dim]")
        console.print("[dim]  'Current' = Latest/ongoing season[/dim]")
        console.print("[dim]  'Last' = Previous completed season[/dim]")
        
        # Get user selection
        console.print("\n")
        choice = console.input("[bold]Select league (1-{}, or 'q' to quit): [/bold]".format(len(league_list)))
        
        if choice.lower() == 'q':
            return None
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(league_list):
                key, league = league_list[idx]
                return (key, league['name'], league)
            else:
                console.print("[red]Invalid selection[/red]")
                return None
        except ValueError:
            console.print("[red]Invalid input[/red]")
            return None
    
    def show_season_menu(self, league_key: str, league_name: str) -> Optional[Dict]:
        """
        Show season selection menu for a league
        
        Args:
            league_key: League key
            league_name: League display name
            
        Returns:
            Season dict with 'id' and 'year' keys, or None if cancelled
        """
        seasons = self.league_mapper.get_league_seasons(league_key)
        
        if not seasons:
            console.print(f"[red]No seasons found for {league_name}[/red]")
            return None
        
        # Get ingestion states
        states = get_all_ingestion_states()
        
        # Create table
        table = Table(title=f"{league_name} - Available Seasons", show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Season", style="cyan")
        table.add_column("Season ID", style="yellow")
        table.add_column("Status", style="green")
        
        for idx, season in enumerate(seasons, 1):
            # Determine status
            state_key = f"{league_key}_{season['id']}"
            status = "✗ Not started"
            
            if state_key in states:
                state_status = states[state_key].get_overall_status()
                if state_status == 'complete':
                    status = "✓ Complete"
                elif state_status == 'in_progress':
                    status = "⚠ Partial"
            
            # Mark latest season
            season_display = season['year']
            if idx == 1:
                season_display += " [LATEST]"
            
            table.add_row(
                str(idx),
                season_display,
                str(season['id']),
                status
            )
        
        console.print("\n")
        console.print(table)
        
        # Get user selection
        console.print("\n")
        choice = console.input("[bold]Select season (1-{}, 'L' for latest, or 'b' to go back): [/bold]".format(len(seasons)))
        
        if choice.lower() == 'b':
            return None
        
        if choice.lower() == 'l':
            return seasons[0]  # Latest is first (sorted by ID desc)
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(seasons):
                return seasons[idx]
            else:
                console.print("[red]Invalid selection[/red]")
                return None
        except ValueError:
            console.print("[red]Invalid input[/red]")
            return None
    
    def select_league_and_season(self) -> Optional[Tuple[str, Dict, Dict]]:
        """
        Interactive selection of league and season
        
        Returns:
            Tuple of (league_key, league_data, season_data) or None if cancelled
        """
        # Select league
        league_result = self.show_league_menu()
        if not league_result:
            return None
        
        league_key, league_name, league_data = league_result
        
        # Select season
        season = self.show_season_menu(league_key, league_name)
        if not season:
            return None
        
        return (league_key, league_data, season)