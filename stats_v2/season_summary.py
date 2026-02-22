"""
Season Summary - Whole season stats with min/max/avg
"""

from typing import Dict, List, Optional
from betting.utils import safe_divide


EUROPEAN_KEYS = {'champions_league', 'europa_league', 'conference_league'}


class SeasonSummary:
    """Generates whole season summary with team and player stats"""

    def __init__(self, team_stats: Dict, league_position: int, total_teams: int,
                 league_fixtures: List[Dict], team_id: int, players: List[Dict]):
        self.team_stats = team_stats
        self.league_position = league_position
        self.total_teams = total_teams
        self.league_fixtures = league_fixtures
        self.team_id = team_id
        self.players = players

    def print_season_summary(self, team_name: str, euro_context_fixtures: Optional[List[Dict]] = None):
        """
        Print complete season summary.

        Args:
            team_name: Display name of the team.
            euro_context_fixtures: If provided, a European context block is appended
                                   showing how the team performs in Europe alongside
                                   their domestic stats.
        """
        matches = self.team_stats['matches']

        wins, draws, losses = self._calculate_wdl()
        points = wins * 3 + draws
        ppg = safe_divide(points, matches)
        win_pct = safe_divide(wins * 100, matches)

        print(f"📊 SEASON SUMMARY ({matches} matches)")
        print("=" * 80)
        print()

        print(f"Record: {wins}W - {draws}D - {losses}L ({win_pct:.1f}% win rate) | "
              f"{points} pts ({ppg:.2f} PPG) | {self.league_position}/{self.total_teams}")

        gf = self.team_stats['goals_scored_avg'] * matches
        ga = self.team_stats['goals_conceded_avg'] * matches
        gd = gf - ga
        gd_str = f"+{gd:.0f}" if gd > 0 else f"{gd:.0f}"

        print(f"Goals:  {gf:.0f} for ({self.team_stats['goals_scored_avg']:.2f}/gm) | "
              f"{ga:.0f} against ({self.team_stats['goals_conceded_avg']:.2f}/gm) | {gd_str} GD")
        print()

        self._print_team_stats()
        self._print_top_performers()

        # European context block — shown when team is selected via domestic league
        if euro_context_fixtures:
            self._print_euro_context(euro_context_fixtures)

    def _calculate_wdl(self) -> tuple:
        wins = draws = losses = 0
        for fixture in self.league_fixtures:
            is_home = fixture.get('homeID') == self.team_id
            home_goals = fixture.get('homeGoalCount', 0)
            away_goals = fixture.get('awayGoalCount', 0)
            if is_home:
                if home_goals > away_goals:
                    wins += 1
                elif home_goals < away_goals:
                    losses += 1
                else:
                    draws += 1
            else:
                if away_goals > home_goals:
                    wins += 1
                elif away_goals < home_goals:
                    losses += 1
                else:
                    draws += 1
        return wins, draws, losses

    def _print_team_stats(self):
        print("TEAM STATS - WHOLE SEASON")
        print("-" * 80)
        print(f"{'STAT':<20} {'TEAM AVG':>10} {'TEAM MIN-MAX':>15} {'MATCH AVG':>12} {'MATCH MIN-MAX':>15}")
        print("-" * 80)

        stats = self._calculate_stat_ranges()

        print(f"{'Goals':<20} {self.team_stats['goals_scored_avg']:>10.1f} "
              f"{stats['gf_min']:>6.0f} - {stats['gf_max']:<7.0f} "
              f"{stats['match_goals_avg']:>12.1f} "
              f"{stats['match_goals_min']:>6.0f} - {stats['match_goals_max']:<7.0f}")

        print(f"{'Shots':<20} {self.team_stats['shots_avg']:>10.1f} "
              f"{stats['shots_min']:>6.0f} - {stats['shots_max']:<7.0f} "
              f"{stats['match_shots_avg']:>12.1f} "
              f"{stats['match_shots_min']:>6.0f} - {stats['match_shots_max']:<7.0f}")

        print(f"{'Shots on Target':<20} {self.team_stats['shots_on_target_avg']:>10.1f} "
              f"{stats['sot_min']:>6.0f} - {stats['sot_max']:<7.0f} "
              f"{stats['match_sot_avg']:>12.1f} "
              f"{stats['match_sot_min']:>6.0f} - {stats['match_sot_max']:<7.0f}")

        print(f"{'Corners':<20} {self.team_stats['corners_avg']:>10.1f} "
              f"{stats['corners_min']:>6.0f} - {stats['corners_max']:<7.0f} "
              f"{stats['match_corners_avg']:>12.1f} "
              f"{stats['match_corners_min']:>6.0f} - {stats['match_corners_max']:<7.0f}")

        print(f"{'Cards':<20} {self.team_stats['cards_avg']:>10.1f} "
              f"{stats['cards_min']:>6.0f} - {stats['cards_max']:<7.0f} "
              f"{stats['match_cards_avg']:>12.1f} "
              f"{stats['match_cards_min']:>6.0f} - {stats['match_cards_max']:<7.0f}")

        print(f"{'Offsides':<20} {self.team_stats['offsides_avg']:>10.1f} "
              f"{stats['offsides_min']:>6.0f} - {stats['offsides_max']:<7.0f} "
              f"{stats['match_offsides_avg']:>12.1f} "
              f"{stats['match_offsides_min']:>6.0f} - {stats['match_offsides_max']:<7.0f}")

        print(f"{'Fouls':<20} {self.team_stats['fouls_avg']:>10.1f} "
              f"{stats['fouls_min']:>6.0f} - {stats['fouls_max']:<7.0f} "
              f"{stats['match_fouls_avg']:>12.1f} "
              f"{stats['match_fouls_min']:>6.0f} - {stats['match_fouls_max']:<7.0f}")

        print(f"{'Possession %':<20} {self.team_stats['possession_avg']:>10.1f} "
              f"{stats['poss_min']:>6.0f} - {stats['poss_max']:<7.0f} "
              f"{'N/A':>12} {'N/A':>15}")

        print()

    def _print_euro_context(self, euro_fixtures: List[Dict]):
        """Append European context block when viewing from domestic selection."""
        print("── EUROPEAN COMPETITION CONTEXT ─────────────────────────────────────────────")
        print()

        n = len(euro_fixtures)
        if n == 0:
            print("  No completed European fixtures found.")
            print()
            return

        wins = draws = losses = 0
        gf = ga = 0
        shots_vals = []
        sot_vals = []
        cards_vals = []

        for f in euro_fixtures:
            is_home = f.get('homeID') == self.team_id
            team_gf = f.get('homeGoalCount', 0) if is_home else f.get('awayGoalCount', 0)
            team_ga = f.get('awayGoalCount', 0) if is_home else f.get('homeGoalCount', 0)
            gf += team_gf
            ga += team_ga
            if team_gf > team_ga:
                wins += 1
            elif team_gf < team_ga:
                losses += 1
            else:
                draws += 1

            prefix = 'team_a' if is_home else 'team_b'
            s = f.get(f'{prefix}_shots', 0)
            st = f.get(f'{prefix}_shotsOnTarget', 0)
            c = f.get(f'{prefix}_cards_num', 0)
            if s >= 0: shots_vals.append(s)
            if st >= 0: sot_vals.append(st)
            if c >= 0: cards_vals.append(c)

        pts = wins * 3 + draws
        ppg = safe_divide(pts, n)
        comp_keys = set(f.get('_league_key', '') for f in euro_fixtures)
        comp_label = ' / '.join(k.replace('_', ' ').title() for k in comp_keys)

        print(f"  Competition:  {comp_label}  ({n} matches)")
        print(f"  Record:       {wins}W-{draws}D-{losses}L | {ppg:.2f} PPG")
        print(f"  Goals:        {safe_divide(gf, n):.2f} scored/gm | {safe_divide(ga, n):.2f} conceded/gm")
        if shots_vals:
            print(f"  Shooting:     {safe_divide(sum(shots_vals), len(shots_vals)):.1f} shots/gm | "
                  f"{safe_divide(sum(sot_vals), len(sot_vals)):.1f} SOT/gm")
        if cards_vals:
            print(f"  Discipline:   {safe_divide(sum(cards_vals), len(cards_vals)):.1f} cards/gm")
        print()
        print("  Note: Teams often rotate for domestic fixtures during European campaigns.")
        print()

    def _calculate_stat_ranges(self) -> Dict:
        team_goals = []; team_shots = []; team_sot = []; team_corners = []
        team_cards = []; team_offsides = []; team_fouls = []; team_poss = []
        match_goals = []; match_shots = []; match_sot = []; match_corners = []
        match_cards = []; match_offsides = []; match_fouls = []

        for fixture in self.league_fixtures:
            is_home = fixture.get('homeID') == self.team_id

            if is_home:
                team_goals.append(fixture.get('homeGoalCount', 0))
                team_shots.append(fixture.get('team_a_shots', 0))
                team_sot.append(fixture.get('team_a_shotsOnTarget', 0))
                team_corners.append(fixture.get('team_a_corners', 0))
                team_cards.append(fixture.get('team_a_cards_num', 0))
                team_offsides.append(fixture.get('team_a_offsides', 0))
                team_fouls.append(fixture.get('team_a_fouls', 0))
                team_poss.append(fixture.get('team_a_possession', 0))
            else:
                team_goals.append(fixture.get('awayGoalCount', 0))
                team_shots.append(fixture.get('team_b_shots', 0))
                team_sot.append(fixture.get('team_b_shotsOnTarget', 0))
                team_corners.append(fixture.get('team_b_corners', 0))
                team_cards.append(fixture.get('team_b_cards_num', 0))
                team_offsides.append(fixture.get('team_b_offsides', 0))
                team_fouls.append(fixture.get('team_b_fouls', 0))
                team_poss.append(fixture.get('team_b_possession', 0))

            match_goals.append(fixture.get('totalGoalCount', 0))
            match_shots.append(fixture.get('team_a_shots', 0) + fixture.get('team_b_shots', 0))
            match_sot.append(fixture.get('team_a_shotsOnTarget', 0) + fixture.get('team_b_shotsOnTarget', 0))
            match_corners.append(fixture.get('totalCornerCount', 0))
            match_cards.append(fixture.get('team_a_cards_num', 0) + fixture.get('team_b_cards_num', 0))
            match_offsides.append(fixture.get('team_a_offsides', 0) + fixture.get('team_b_offsides', 0))
            match_fouls.append(fixture.get('team_a_fouls', 0) + fixture.get('team_b_fouls', 0))

        def safe_min(lst): return min([v for v in lst if v >= 0], default=0)
        def safe_max(lst): return max([v for v in lst if v >= 0], default=0)
        def safe_avg(lst):
            vals = [v for v in lst if v >= 0]
            return safe_divide(sum(vals), len(vals))

        return {
            'gf_min': safe_min(team_goals),         'gf_max': safe_max(team_goals),
            'shots_min': safe_min(team_shots),       'shots_max': safe_max(team_shots),
            'sot_min': safe_min(team_sot),           'sot_max': safe_max(team_sot),
            'corners_min': safe_min(team_corners),   'corners_max': safe_max(team_corners),
            'cards_min': safe_min(team_cards),       'cards_max': safe_max(team_cards),
            'offsides_min': safe_min(team_offsides), 'offsides_max': safe_max(team_offsides),
            'fouls_min': safe_min(team_fouls),       'fouls_max': safe_max(team_fouls),
            'poss_min': safe_min(team_poss),         'poss_max': safe_max(team_poss),

            'match_goals_min': safe_min(match_goals),   'match_goals_max': safe_max(match_goals),   'match_goals_avg': safe_avg(match_goals),
            'match_shots_min': safe_min(match_shots),   'match_shots_max': safe_max(match_shots),   'match_shots_avg': safe_avg(match_shots),
            'match_sot_min': safe_min(match_sot),       'match_sot_max': safe_max(match_sot),       'match_sot_avg': safe_avg(match_sot),
            'match_corners_min': safe_min(match_corners),'match_corners_max': safe_max(match_corners),'match_corners_avg': safe_avg(match_corners),
            'match_cards_min': safe_min(match_cards),   'match_cards_max': safe_max(match_cards),   'match_cards_avg': safe_avg(match_cards),
            'match_offsides_min': safe_min(match_offsides),'match_offsides_max': safe_max(match_offsides),'match_offsides_avg': safe_avg(match_offsides),
            'match_fouls_min': safe_min(match_fouls),   'match_fouls_max': safe_max(match_fouls),   'match_fouls_avg': safe_avg(match_fouls),
        }

    def _print_top_performers(self):
        print("TOP SEASON PERFORMERS")
        print("-" * 80)

        scorers = sorted(
            [p for p in self.players if p.get('goals_overall', 0) > 0 and p.get('minutes_played_overall', 0) >= 450],
            key=lambda p: p['goals_overall'], reverse=True
        )
        assisters = sorted(
            [p for p in self.players if p.get('assists_overall', 0) > 0 and p.get('minutes_played_overall', 0) >= 450],
            key=lambda p: p['assists_overall'], reverse=True
        )
        carded = sorted(
            [p for p in self.players if p.get('cards_overall', 0) > 0 and p.get('minutes_played_overall', 0) >= 450],
            key=lambda p: p['cards_overall'], reverse=True
        )

        print("GOALS (Season Total)")
        for i, p in enumerate(scorers[:3], 1):
            name = p.get('known_as', p.get('full_name', 'Unknown'))
            goals = p['goals_overall']
            mins = p['minutes_played_overall']
            per90 = safe_divide(goals * 90, mins)
            print(f"  {i}. {name:<25} {goals:>2} goals ({per90:.2f} per 90) - {mins} mins")
        print()

        print("ASSISTS (Season Total)")
        for i, p in enumerate(assisters[:3], 1):
            name = p.get('known_as', p.get('full_name', 'Unknown'))
            assists = p['assists_overall']
            mins = p['minutes_played_overall']
            per90 = safe_divide(assists * 90, mins)
            print(f"  {i}. {name:<25} {assists:>2} assists ({per90:.2f} per 90) - {mins} mins")
        print()

        print("CARDS (Season Total - Discipline Risk)")
        for i, p in enumerate(carded[:3], 1):
            name = p.get('known_as', p.get('full_name', 'Unknown'))
            cards = p['cards_overall']
            mins = p['minutes_played_overall']
            per90 = safe_divide(cards * 90, mins)
            risk = "⚠️  RISK" if cards >= 8 else ""
            print(f"  {i}. {name:<25} {cards:>2} cards ({per90:.2f} per 90) - {mins} mins {risk}")
        print()