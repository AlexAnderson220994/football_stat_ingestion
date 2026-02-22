"""
Main ingestion orchestration
"""

import sys
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel

from .api_client import APIClient
from .rate_limiter import RateLimiter
from .league_mapper import LeagueMapper
from .league_selector import LeagueSelector
from .data_manager import DataManager
from .state_manager import IngestionState, get_all_ingestion_states
from .team_aggregator import aggregate_teams
from .collectors import (
    LeagueCollector,
    TeamCollector,
    MatchCollector,
    PlayerCollector,
    RefereeCollector,
    StatsCollector,
    H2HCollector,
    MatchDetailsCollector
)

console = Console()


def show_main_menu() -> int:
    """
    Show main menu and get user choice
    
    Returns:
        User's menu choice (1-4)
    """
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]Football Stats Ingestion System[/bold cyan]\n"
        "[dim]Rate Limit: 1800 requests/hour[/dim]",
        border_style="cyan"
    ))
    
    console.print("\n[bold]Select ingestion mode:[/bold]")
    console.print("  1. Ingest single league/season (full or incremental)")
    console.print("  2. Update all leagues (current season only)")
    console.print("  3. View ingestion status")
    console.print("  4. Refresh league cache")
    console.print("  5. Aggregate team data (post-ingestion)")
    console.print("  6. Exit")
    
    choice = console.input("\n[bold]Your choice (1-6): [/bold]")
    
    try:
        return int(choice)
    except ValueError:
        return 0


def ingest_single_league():
    """
    Ingest a single league/season with interactive selection
    """
    # Initialize components
    rate_limiter = RateLimiter()
    api_client = APIClient(rate_limiter)
    league_mapper = LeagueMapper(api_client)
    league_selector = LeagueSelector(league_mapper)
    
    # Show rate limit status
    console.print("\n")
    status = rate_limiter.get_status()
    console.print(f"[dim]Rate Limit: {status['calls_this_hour']}/{status['requests_per_hour']} used, "
                 f"{status['remaining_requests']} remaining[/dim]")
    
    # Select league and season
    selection = league_selector.select_league_and_season()
    
    if not selection:
        console.print("[yellow]Selection cancelled[/yellow]")
        return
    
    league_key, league_data, season = selection
    
    console.print(f"\n[bold green]Selected:[/bold green] {league_data['name']} - {season['year']}")
    console.print(f"[dim]Season ID: {season['id']}[/dim]")
    
    # Initialize managers and collectors
    data_manager = DataManager(league_key, season['id'], season['year'])
    state = IngestionState(league_key, season['id'], season['year'])
    
    # Check existing state
    overall_status = state.get_overall_status()
    
    if overall_status == 'complete':
        console.print("\n[yellow]⚠ This season has already been fully ingested.[/yellow]")
        update = console.input("[bold]Update/re-ingest anyway? (y/n): [/bold]")
        if update.lower() != 'y':
            return
    elif overall_status == 'in_progress':
        console.print("\n[yellow]ℹ Previous ingestion was interrupted. Will resume from last checkpoint.[/yellow]")
    
    # Show ingestion plan
    console.print("\n[bold cyan]Ingestion Plan:[/bold cyan]")
    collections = state.state['collections']
    
    for name, coll in collections.items():
        status_str = coll.get('status', 'pending')
        
        if status_str == 'complete':
            console.print(f"  ✓ {name}: Already complete")
        elif status_str == 'in_progress':
            fetched = coll.get('fetched', 0)
            total = coll.get('total', '?')
            console.print(f"  ⚠ {name}: Partial ({fetched}/{total})")
        else:
            console.print(f"  ○ {name}: Pending")
    
    # Confirm
    console.print("\n")
    confirm = console.input("[bold]Start ingestion? (y/n): [/bold]")
    
    if confirm.lower() != 'y':
        console.print("[yellow]Ingestion cancelled[/yellow]")
        return
    
    # Start ingestion
    console.print("\n[bold green]Starting ingestion...[/bold green]")
    start_time = datetime.now()
    
    try:
        # Initialize collectors
        league_collector = LeagueCollector(api_client, data_manager, state)
        team_collector = TeamCollector(api_client, data_manager, state)
        match_collector = MatchCollector(api_client, data_manager, state)
        player_collector = PlayerCollector(api_client, data_manager, state)
        referee_collector = RefereeCollector(api_client, data_manager, state)
        match_details_collector = MatchDetailsCollector(api_client, data_manager, state)
        stats_collector = StatsCollector(api_client)
        h2h_collector = H2HCollector(data_manager, state)
        
        # Run collectors in order
        league_collector.collect_all()
        team_collector.collect_all()
        match_collector.collect_all()
        match_details_collector.collect_all()  # NEW: Collect detailed match data
        player_collector.collect_all()
        referee_collector.collect_all()
        h2h_collector.collect_all()
        stats_collector.collect_all()
        
        # Mark complete
        state.mark_complete()
        
        # Show summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        console.print("\n")
        console.print(Panel.fit(
            f"[bold green]✓ Ingestion Complete![/bold green]\n\n"
            f"League: {league_data['name']}\n"
            f"Season: {season['year']}\n"
            f"Duration: {int(duration // 60)}m {int(duration % 60)}s\n"
            f"API Calls: {state.state['total_api_calls']}",
            border_style="green"
        ))
        
        # Show final rate limit status
        final_status = rate_limiter.get_status()
        console.print(f"\n[dim]Rate Limit: {final_status['calls_this_hour']}/{final_status['requests_per_hour']} used, "
                     f"{final_status['remaining_requests']} remaining[/dim]")
        
        # Ask about team aggregation
        console.print("\n[bold cyan]Team Aggregation[/bold cyan]")
        console.print("Would you like to aggregate team data across all competitions now?")
        console.print("[dim]This combines data for teams playing in multiple leagues (no API calls)[/dim]")
        
        aggregate = console.input("\n[bold]Aggregate team data? (y/n): [/bold]")
        
        if aggregate.lower() == 'y':
            run_team_aggregation()
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Ingestion interrupted by user[/yellow]")
        console.print("[green]💾 Progress has been saved. Run again to resume.[/green]")
        raise
    except Exception as e:
        console.print(f"\n[red]✗ Error during ingestion: {e}[/red]")
        console.print("[yellow]💾 Progress has been saved. Run again to resume.[/yellow]")
        raise


def update_all_leagues():
    """
    Update all leagues to their current season
    """
    console.print("\n[bold cyan]Updating all leagues (current season only)...[/bold cyan]\n")
    
    # Initialize components
    rate_limiter = RateLimiter()
    api_client = APIClient(rate_limiter)
    league_mapper = LeagueMapper(api_client)
    
    # Fetch all leagues
    console.print("[yellow]Loading league data...[/yellow]")
    leagues_data = league_mapper.fetch_and_map_leagues()
    
    # Show rate limit status
    console.print("\n")
    status = rate_limiter.get_status()
    console.print(f"[dim]Rate Limit: {status['calls_this_hour']}/{status['requests_per_hour']} used, "
                 f"{status['remaining_requests']} remaining[/dim]\n")
    
    # Confirm before proceeding
    console.print(f"[bold]This will update the latest season for {len(leagues_data)} leagues.[/bold]")
    console.print("[yellow]This may use significant API calls.[/yellow]")
    confirm = console.input("\n[bold]Proceed with bulk update? (y/n): [/bold]")
    
    if confirm.lower() != 'y':
        console.print("[yellow]Bulk update cancelled[/yellow]")
        return
    
    successful = 0
    failed = 0
    skipped = 0
    
    for idx, (league_key, league_data) in enumerate(leagues_data.items(), 1):
        console.print(f"\n[cyan]{'='*60}[/cyan]")
        console.print(f"[bold cyan]League {idx}/{len(leagues_data)}: {league_data['name']}[/bold cyan]")
        console.print(f"[cyan]{'='*60}[/cyan]")
        
        # Get latest season using the mapper method (ensures proper sorting)
        latest_season = league_mapper.get_latest_season(league_key)
        
        if not latest_season:
            console.print("[yellow]⚠ No seasons available, skipping[/yellow]")
            skipped += 1
            continue
        
        console.print(f"[bold]Season:[/bold] {latest_season['year']} (ID: {latest_season['id']})")
        
        try:
            # Initialize managers
            data_manager = DataManager(league_key, latest_season['id'], latest_season['year'])
            state = IngestionState(league_key, latest_season['id'], latest_season['year'])
            
            # Initialize collectors
            league_collector = LeagueCollector(api_client, data_manager, state)
            team_collector = TeamCollector(api_client, data_manager, state)
            match_collector = MatchCollector(api_client, data_manager, state)
            player_collector = PlayerCollector(api_client, data_manager, state)
            referee_collector = RefereeCollector(api_client, data_manager, state)
            match_details_collector = MatchDetailsCollector(api_client, data_manager, state)
            h2h_collector = H2HCollector(data_manager, state)
            
            # Run collectors
            league_collector.collect_all()
            team_collector.collect_all()
            match_collector.collect_all()
            match_details_collector.collect_all()
            player_collector.collect_all()
            referee_collector.collect_all()
            h2h_collector.collect_all()
            
            # Mark complete
            state.mark_complete()
            
            console.print(f"[green]✓ {league_data['name']} updated successfully[/green]")
            successful += 1
            
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠ Bulk update interrupted by user[/yellow]")
            console.print(f"[green]✓ Completed: {successful}[/green]")
            console.print(f"[red]✗ Failed: {failed}[/red]")
            console.print(f"[yellow]⚠ Skipped: {skipped}[/yellow]")
            raise
        except Exception as e:
            console.print(f"[red]✗ Failed to update {league_data['name']}: {e}[/red]")
            failed += 1
            continue
    
    # Final summary
    console.print(f"\n[cyan]{'='*60}[/cyan]")
    console.print("[bold cyan]BULK UPDATE COMPLETE[/bold cyan]")
    console.print(f"[cyan]{'='*60}[/cyan]")
    console.print(f"[green]✓ Successful: {successful}[/green]")
    console.print(f"[red]✗ Failed: {failed}[/red]")
    console.print(f"[yellow]⚠ Skipped: {skipped}[/yellow]")
    
    # Show final rate limit
    final_status = rate_limiter.get_status()
    console.print(f"\n[dim]Rate Limit: {final_status['calls_this_hour']}/{final_status['requests_per_hour']} used, "
                 f"{final_status['remaining_requests']} remaining[/dim]")


def view_ingestion_status():
    """
    View status of all ingestions
    """
    console.print("\n[bold cyan]Ingestion Status[/bold cyan]\n")
    
    states = get_all_ingestion_states()
    
    if not states:
        console.print("[yellow]No ingestions found[/yellow]")
        return
    
    # Create table
    from rich.table import Table
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("League", style="cyan")
    table.add_column("Season", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Progress", style="blue")
    table.add_column("API Calls", style="dim")
    
    for key, state in sorted(states.items()):
        summary = state.get_summary()
        
        # Calculate overall progress
        collections = summary['collections']
        complete_count = sum(1 for c in collections.values() if c['status'] == 'complete')
        total_count = len(collections)
        progress = f"{complete_count}/{total_count}"
        
        # Status display
        status = summary['status']
        if status == 'complete':
            status_display = "✓ Complete"
        elif status == 'in_progress':
            status_display = "⚠ In Progress"
        else:
            status_display = "○ Not Started"
        
        table.add_row(
            summary['league'].replace('_', ' ').title(),
            summary['season_year'],
            status_display,
            progress,
            str(summary['total_api_calls'])
        )
    
    console.print(table)


def refresh_league_cache():
    """
    Force refresh the league cache
    """
    console.print("\n[bold cyan]Refreshing league cache...[/bold cyan]")
    
    rate_limiter = RateLimiter()
    api_client = APIClient(rate_limiter)
    league_mapper = LeagueMapper(api_client)
    
    try:
        league_mapper.refresh_cache()
        console.print("[green]✓ League cache refreshed successfully[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to refresh cache: {e}[/red]")


def run_team_aggregation():
    """
    Run team data aggregation across all competitions
    """
    console.print("\n[bold cyan]Aggregating Team Data[/bold cyan]")
    console.print("[dim]This will combine team data across all competitions...[/dim]\n")
    
    try:
        start_time = datetime.now()
        
        summary = aggregate_teams()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        console.print(f"\n[bold green]✓ Team aggregation complete![/bold green]")
        console.print(f"[dim]Duration: {int(duration)}s[/dim]")
        console.print(f"\n[cyan]Team data available in: data/teams/[/cyan]")
        
    except Exception as e:
        console.print(f"\n[red]✗ Error during aggregation: {e}[/red]")
        import traceback
        traceback.print_exc()


def main():
    """
    Main entry point for ingestion system
    """
    try:
        while True:
            choice = show_main_menu()
            
            if choice == 1:
                ingest_single_league()
            elif choice == 2:
                update_all_leagues()
            elif choice == 3:
                view_ingestion_status()
            elif choice == 4:
                refresh_league_cache()
            elif choice == 5:
                run_team_aggregation()
            elif choice == 6:
                console.print("\n[cyan]Goodbye![/cyan]")
                break
            else:
                console.print("\n[red]Invalid choice, please try again[/red]")
            
            # Wait for user before showing menu again
            if choice in [1, 2, 3, 4, 5]:
                console.input("\n[dim]Press Enter to continue...[/dim]")
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()