#!/usr/bin/env python3
"""
Team Stats Analyzer V2
Match Summary Focus - Detailed breakdown of last 10 + H2H
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from betting import DataLoader, StatCalculator
from stats_v2 import (
    SeasonSummary,
    MatchBreakdown,
    H2HAnalysis,
    MomentumAnalyzerV2,
    EuropeanSummary,
    FixtureAnalysis,
)

EUROPEAN_KEYS = {'champions_league', 'europa_league', 'europa_conference_league'}

COMP_TAGS = {
    'champions_league':         '[UCL]',
    'europa_league':            '[UEL]',
    'europa_conference_league': '[UECL]',
}

EURO_PHASES = {
    'champions_league':         'Champions League',
    'europa_league':            'Europa League',
    'europa_conference_league': 'Europa Conference League',
}


# ── League selection ──────────────────────────────────────────────────────────

def select_league(loader: DataLoader) -> Optional[Dict]:
    leagues = loader.get_available_leagues()

    if not leagues:
        print("No leagues found. Run data ingestion first.")
        return None

    print("=" * 80)
    print("⚽ TEAM STATS ANALYZER V2 - MATCH SUMMARY FOCUS")
    print("=" * 80)
    print()
    print("📊 AVAILABLE LEAGUES")
    print()

    domestic = [l for l in leagues if l['key'] not in EUROPEAN_KEYS]
    european = [l for l in leagues if l['key'] in EUROPEAN_KEYS]

    all_listed = []

    if domestic:
        print("  DOMESTIC")
        for league in domestic:
            all_listed.append(league)
            completed = league.get('completed_gameweeks', 0)
            print(f"  {len(all_listed):>2}. {league['name']} ({completed} GW)")
        print()

    if european:
        print("  EUROPEAN")
        for league in european:
            all_listed.append(league)
            completed = league.get('completed_gameweeks', 0)
            gw_str = f"{completed} GW" if completed > 0 else "Knockout only"
            print(f"  {len(all_listed):>2}. {league['name']} ({gw_str})")
        print()

    try:
        choice = int(input(f"Select competition (1-{len(all_listed)}): "))
        return all_listed[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection")
        return None


# ── European phase selection ──────────────────────────────────────────────────

def select_euro_phase(league: Dict, loader: DataLoader) -> Optional[str]:
    """
    For European competitions, ask user whether they want league phase or knockouts.
    Returns 'league_phase', 'knockouts', or None if invalid.
    """
    league_key = league['key']
    season_id  = league['season_id']

    all_matches = loader.load_all_matches(league_key, season_id)
    has_league_phase = any(m.get('game_week', 0) >= 1 for m in all_matches)
    has_knockouts    = any(m.get('game_week', 0) == 0 for m in all_matches)

    print()
    print(f"📊 {league['name'].upper()} - SELECT PHASE")
    print()

    options = []
    if has_league_phase:
        options.append(('league_phase', 'League Phase'))
    if has_knockouts:
        options.append(('knockouts', 'Knockouts'))

    if not options:
        print("No match data found for this competition.")
        return None

    for i, (key, label) in enumerate(options, 1):
        print(f"  {i}. {label}")
    print()

    try:
        choice = int(input(f"Select phase (1-{len(options)}): "))
        return options[choice - 1][0]
    except (ValueError, IndexError):
        print("Invalid selection")
        return None


# ── League table display ──────────────────────────────────────────────────────

def print_league_table(league_table: dict, league_name: str) -> List[Dict]:
    print()
    print("=" * 80)
    print(f"📊 LEAGUE TABLE - {league_name.upper()}")
    print("=" * 80)
    print()

    if not league_table:
        print("League table not available")
        return []

    table_data = league_table.get('data', {}).get('league_table', [])
    if not table_data:
        print("No table data available")
        return []

    table_data.sort(key=lambda x: x.get('position', 999))

    print(f"{'Pos':<4} {'Team':<30} {'P':<4} {'GF':<4} {'GA':<4} {'GD':<6} {'Pts':<4}")
    print("-" * 80)

    for team in table_data[:20]:
        pos    = team.get('position', '-')
        name   = team.get('name', 'Unknown')[:28]
        played = team.get('matchesPlayed', 0)
        gf     = team.get('seasonGoals', 0)
        ga     = team.get('seasonConceded', 0)
        gd     = team.get('seasonGoalDifference', 0)
        pts    = team.get('points', 0)
        gd_str = f"+{gd}" if gd > 0 else str(gd)
        print(f"{pos:<4} {name:<30} {played:<4} {gf:<4} {ga:<4} {gd_str:<6} {pts:<4}")

    print()
    return table_data


# ── European league phase team list ──────────────────────────────────────────

def print_euro_league_phase_teams(loader: DataLoader, league_key: str, season_id: int) -> List[Dict]:
    """
    Build a team list from league phase fixtures (game_week >= 1).
    Returns list of dicts with team_id and team_name.
    """
    all_matches = loader.load_all_matches(league_key, season_id)
    league_phase = [m for m in all_matches if m.get('game_week', 0) >= 1]

    seen = {}
    for m in league_phase:
        for id_key, name_key in [('homeID', 'home_name'), ('awayID', 'away_name')]:
            tid   = m.get(id_key)
            tname = m.get(name_key)
            if tid and tname and tid not in seen:
                seen[tid] = tname

    teams = [{'id': tid, 'name': name} for tid, name in seen.items()]
    teams.sort(key=lambda t: t['name'])

    print()
    print("=" * 80)
    print(f"📊 LEAGUE PHASE TEAMS")
    print("=" * 80)
    print()

    for i, t in enumerate(teams, 1):
        print(f"  {i:>2}. {t['name']}")
    print()

    return teams


# ── Knockout fixture list ─────────────────────────────────────────────────────

def select_knockout_fixture(loader: DataLoader, league_key: str, season_id: int) -> Optional[Dict]:
    """
    Show upcoming incomplete knockout fixtures (game_week == 0, status incomplete/fixture).
    User selects one. Returns the fixture dict or None.
    """
    all_matches = loader.load_all_matches(league_key, season_id)
    upcoming = [
        m for m in all_matches
        if m.get('game_week', 0) == 0
        and m.get('status') in ['incomplete', 'fixture']
    ]
    upcoming.sort(key=lambda m: m.get('date_unix', 0))

    print()
    print("=" * 80)
    print("📊 UPCOMING KNOCKOUT FIXTURES")
    print("=" * 80)
    print()

    if not upcoming:
        print("No upcoming knockout fixtures found.")
        print("The draw may not have taken place yet.")
        print()
        return None

    from betting.utils import format_date
    for i, m in enumerate(upcoming, 1):
        home = m.get('home_name', 'TBD')
        away = m.get('away_name', 'TBD')
        date = format_date(m.get('date_unix', 0))
        print(f"  {i:>2}. {home} vs {away}  ({date})")
    print()

    try:
        choice = int(input(f"Select fixture (1-{len(upcoming)}): "))
        return upcoming[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection")
        return None


# ── Team selection helpers ────────────────────────────────────────────────────

def select_team_from_table(table_data: List[Dict]) -> Optional[Dict]:
    if not table_data:
        return None
    try:
        choice = int(input(f"Select team (1-{len(table_data)}): "))
        return table_data[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection")
        return None


def select_team_from_list(teams: List[Dict]) -> Optional[Dict]:
    if not teams:
        return None
    try:
        choice = int(input(f"Select team (1-{len(teams)}): "))
        return teams[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection")
        return None


# ── Domestic analysis ─────────────────────────────────────────────────────────

def analyze_domestic(loader: DataLoader, league_key: str, season_id: int,
                     team_id: int, team_name: str,
                     league_position: int, total_teams: int):
    """
    Domestic league selection flow.
    League stats are primary. European fixtures mixed into last 10 by date.
    European context block appended to season summary if team plays in Europe.
    """
    print()
    print("=" * 80)
    print(f"⚽ {team_name.upper()} - MATCH SUMMARY ANALYSIS")
    print("=" * 80)
    print()

    fixtures_data = loader.load_team_fixtures(team_id)
    if not fixtures_data:
        print("No fixture data available")
        return

    all_fixtures = fixtures_data.get('fixtures', [])

    league_fixtures = [
        f for f in all_fixtures
        if f.get('_league_key') == league_key and f.get('status') == 'complete'
    ]

    if not league_fixtures:
        print("No completed league fixtures found")
        return

    euro_fixtures_completed = [
        f for f in all_fixtures
        if f.get('_league_key') in EUROPEAN_KEYS and f.get('status') == 'complete'
    ]

    # Stats based on league only
    calculator   = StatCalculator()
    overall_stats = calculator.calculate_team_averages(team_id, league_fixtures, is_home=None)

    # Players
    players = loader.load_team_players(league_key, season_id, team_id) or []

    # All players across teams seen in league fixtures (for name lookup)
    team_ids = set()
    for f in league_fixtures:
        team_ids.add(f.get('homeID'))
        team_ids.add(f.get('awayID'))
    all_league_players = []
    for tid in team_ids:
        tp = loader.load_team_players(league_key, season_id, tid)
        if tp:
            all_league_players.extend(tp)

    # 1. Season summary (league primary, euro context if applicable)
    summary = SeasonSummary(overall_stats, league_position, total_teams,
                            league_fixtures, team_id, players)
    summary.print_season_summary(
        team_name,
        euro_context_fixtures=euro_fixtures_completed if euro_fixtures_completed else None
    )

    # 2. Last 10 — domestic fixtures plus any European games within that date window
    league_fixtures_sorted = sorted(league_fixtures, key=lambda f: f.get('date_unix', 0))
    last_10_league = league_fixtures_sorted[-10:]

    if last_10_league:
        window_start = last_10_league[0].get('date_unix', 0)
        euro_in_window = [
            f for f in euro_fixtures_completed
            if f.get('date_unix', 0) >= window_start
        ]
        combined = last_10_league + euro_in_window
        combined.sort(key=lambda f: f.get('date_unix', 0))
    else:
        combined = []

    # Load match details for combined set, injecting _league_key from fixture
    combined_details = []
    for fixture in combined:
        match_id   = fixture.get('id')
        fkey       = fixture.get('_league_key', league_key)
        fsid       = fixture.get('_season_id', season_id)
        detail     = loader.load_match_details(fkey, fsid, match_id)
        if detail:
            detail['_league_key'] = fkey
            combined_details.append(detail)

    if combined_details:
        breakdown = MatchBreakdown(team_id, team_name, all_league_players)
        breakdown.print_last_n_breakdown(combined_details, len(combined_details))

    # 3. H2H — next league fixture only
    all_league_fixtures = [f for f in all_fixtures if f.get('_league_key') == league_key]
    upcoming = sorted(
        [f for f in all_league_fixtures if f.get('status') in ['incomplete', 'fixture']],
        key=lambda f: f.get('date_unix', 0)
    )

    if upcoming:
        next_match = upcoming[0]
        is_home    = next_match.get('homeID') == team_id
        opp_id     = next_match.get('awayID') if is_home else next_match.get('homeID')
        opp_name   = next_match.get('away_name') if is_home else next_match.get('home_name')

        all_matches = loader.load_all_matches(league_key, season_id)
        h2h_matches = sorted(
            [m for m in all_matches
             if m.get('status') == 'complete'
             and {m.get('homeID'), m.get('awayID')} == {team_id, opp_id}],
            key=lambda m: m.get('date_unix', 0)
        )

        if h2h_matches:
            most_recent = h2h_matches[-1]
            match_id    = most_recent.get('id')
            h2h_detail  = loader.load_match_details(league_key, season_id, match_id)
            if h2h_detail:
                h2h_analyzer = H2HAnalysis(team_id, team_name, all_league_players)
                h2h_analyzer.print_h2h_analysis(h2h_detail, opp_name)

    # 4. Momentum — league primary, euro fixtures passed for comparison block
    momentum = MomentumAnalyzerV2(
        league_fixtures,
        team_id,
        overall_stats['goals_scored_avg'],
        overall_stats['goals_conceded_avg'],
        overall_stats['shots_avg'],
        overall_stats['shots_on_target_avg'],
        overall_stats['cards_avg'],
        overall_stats['corners_avg'],
        overall_stats.get('fouls_avg', 0),
        euro_fixtures=euro_fixtures_completed if euro_fixtures_completed else None,
    )
    momentum.print_momentum()


# ── European league phase analysis ───────────────────────────────────────────

def analyze_european_league_phase(loader: DataLoader, league_key: str, season_id: int,
                                   team_id: int, team_name: str):
    """
    European league phase selection flow.
    European stats are primary. Domestic form as context.
    """
    print()
    print("=" * 80)
    print(f"⚽ {team_name.upper()} - {EURO_PHASES.get(league_key, 'EUROPEAN').upper()} ANALYSIS")
    print("=" * 80)
    print()

    fixtures_data = loader.load_team_fixtures(team_id)
    if not fixtures_data:
        print("No fixture data available")
        return

    all_fixtures = fixtures_data.get('fixtures', [])

    euro_fixtures = [
        f for f in all_fixtures
        if f.get('_league_key') == league_key
        and f.get('game_week', 0) >= 1
        and f.get('status') == 'complete'
    ]

    domestic_fixtures = [
        f for f in all_fixtures
        if f.get('_league_key') not in EUROPEAN_KEYS
        and f.get('status') == 'complete'
    ]

    # Players — try euro league first, fall back to domestic
    players = loader.load_team_players(league_key, season_id, team_id) or []
    if not players and domestic_fixtures:
        dom_key = domestic_fixtures[0].get('_league_key')
        dom_sid = domestic_fixtures[0].get('_season_id')
        if dom_key and dom_sid:
            players = loader.load_team_players(dom_key, dom_sid, team_id) or []

    euro_label = f"{EURO_PHASES.get(league_key, 'EUROPEAN').upper()} - LEAGUE PHASE"

    # 1. European summary (primary) with domestic context
    euro_summary = EuropeanSummary(team_id, players)
    euro_summary.print_european_summary(
        team_name,
        euro_fixtures,
        domestic_fixtures=domestic_fixtures,
        euro_label=euro_label,
    )

    # 2. Last 10 all competitions interleaved
    all_completed = sorted(
        [f for f in all_fixtures if f.get('status') == 'complete'],
        key=lambda f: f.get('date_unix', 0)
    )
    last_10 = all_completed[-10:]

    all_players = list(players)
    team_ids = set()
    for f in last_10:
        team_ids.add(f.get('homeID'))
        team_ids.add(f.get('awayID'))
    for tid in team_ids:
        if tid != team_id:
            tp = loader.load_team_players(league_key, season_id, tid)
            if tp:
                all_players.extend(tp)

    last_10_details = []
    for fixture in last_10:
        match_id = fixture.get('id')
        fkey     = fixture.get('_league_key', league_key)
        fsid     = fixture.get('_season_id', season_id)
        detail   = loader.load_match_details(fkey, fsid, match_id)
        if detail:
            detail['_league_key'] = fkey
            last_10_details.append(detail)

    if last_10_details:
        breakdown = MatchBreakdown(team_id, team_name, all_players)
        breakdown.print_last_n_breakdown(last_10_details, len(last_10_details))

    # 3. H2H — next European fixture (any phase)
    upcoming_euro = sorted(
        [f for f in all_fixtures
         if f.get('_league_key') == league_key
         and f.get('status') in ['incomplete', 'fixture']],
        key=lambda f: f.get('date_unix', 0)
    )

    if upcoming_euro:
        next_match = upcoming_euro[0]
        is_home    = next_match.get('homeID') == team_id
        opp_id     = next_match.get('awayID') if is_home else next_match.get('homeID')
        opp_name   = next_match.get('away_name') if is_home else next_match.get('home_name')
        comp_tag   = COMP_TAGS.get(league_key, '')

        all_euro_matches = loader.load_all_matches(league_key, season_id)
        h2h_matches = sorted(
            [m for m in all_euro_matches
             if m.get('status') == 'complete'
             and {m.get('homeID'), m.get('awayID')} == {team_id, opp_id}],
            key=lambda m: m.get('date_unix', 0)
        )

        if h2h_matches:
            most_recent = h2h_matches[-1]
            h2h_detail  = loader.load_match_details(league_key, season_id, most_recent.get('id'))
            if h2h_detail:
                h2h_analyzer = H2HAnalysis(team_id, team_name, all_players)
                h2h_analyzer.print_h2h_analysis(h2h_detail, opp_name, competition_label=comp_tag)
        else:
            print("=" * 80)
            print(f"🔥 HEAD-TO-HEAD vs {opp_name.upper()}")
            print("=" * 80)
            print()
            print(f"  No previous meetings in this competition this season.")
            print()

    # 4. Momentum — euro fixtures primary, domestic as comparison
    if euro_fixtures:
        calculator    = StatCalculator()
        euro_stats    = calculator.calculate_team_averages(team_id, euro_fixtures, is_home=None)

        momentum = MomentumAnalyzerV2(
            euro_fixtures,
            team_id,
            euro_stats['goals_scored_avg'],
            euro_stats['goals_conceded_avg'],
            euro_stats['shots_avg'],
            euro_stats['shots_on_target_avg'],
            euro_stats['cards_avg'],
            euro_stats['corners_avg'],
            euro_stats.get('fouls_avg', 0),
            euro_fixtures=domestic_fixtures if domestic_fixtures else None,
        )
        momentum.print_momentum()


# ── Knockout fixture analysis ─────────────────────────────────────────────────

def analyze_knockout_fixture(loader: DataLoader, calculator: StatCalculator,
                              fixture: Dict, league_key: str, season_id: int):
    """Run head-to-head fixture analysis for a knockout match."""
    home_id = fixture.get('homeID')
    away_id = fixture.get('awayID')

    home_fixtures_data = loader.load_team_fixtures(home_id)
    away_fixtures_data = loader.load_team_fixtures(away_id)

    home_all = home_fixtures_data.get('fixtures', []) if home_fixtures_data else []
    away_all  = away_fixtures_data.get('fixtures', []) if away_fixtures_data else []

    analyzer = FixtureAnalysis(loader, calculator)
    analyzer.print_fixture_analysis(
        fixture,
        euro_key=league_key,
        euro_season_id=season_id,
        all_fixtures_home=home_all,
        all_fixtures_away=away_all,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    loader     = DataLoader()
    calculator = StatCalculator()

    league = select_league(loader)
    if not league:
        return

    league_key = league['key']
    season_id  = league['season_id']
    league_name = league['name']

    print()
    print(f"✓ Selected: {league_name}")

    # European competition
    if league_key in EUROPEAN_KEYS:
        phase = select_euro_phase(league, loader)
        if not phase:
            return

        if phase == 'knockouts':
            fixture = select_knockout_fixture(loader, league_key, season_id)
            if not fixture:
                return
            analyze_knockout_fixture(loader, calculator, fixture, league_key, season_id)

        else:  # league_phase
            teams = print_euro_league_phase_teams(loader, league_key, season_id)
            if not teams:
                return
            team = select_team_from_list(teams)
            if not team:
                return
            analyze_european_league_phase(
                loader, league_key, season_id,
                team['id'], team['name']
            )

    # Domestic league
    else:
        league_table = loader.load_league_table(league_key, season_id)
        table_data   = print_league_table(league_table, league_name)
        if not table_data:
            return

        team = select_team_from_table(table_data)
        if not team:
            return

        analyze_domestic(
            loader, league_key, season_id,
            team['id'], team['name'],
            team.get('position', 0),
            len(table_data)
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)