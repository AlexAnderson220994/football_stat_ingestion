"""
European Summary - European competition season summary with domestic context
"""

from typing import Dict, List, Optional
from betting.utils import safe_divide


EUROPEAN_KEYS = {'champions_league', 'europa_league', 'europa_conference_league'}


class EuropeanSummary:
    """
    European competition season summary.
    Primary: European stats. Secondary: Domestic context block.
    """

    def __init__(self, team_id: int, players: List[Dict]):
        self.team_id = team_id
        self.players = players

    def print_european_summary(
        self,
        team_name: str,
        euro_fixtures: List[Dict],
        domestic_fixtures: Optional[List[Dict]] = None,
        euro_label: str = "EUROPEAN",
    ):
        print(f"📊 {euro_label} SUMMARY ({len(euro_fixtures)} matches)")
        print("=" * 80)
        print()

        if not euro_fixtures:
            print("No European fixture data available.")
            print()
            return

        wins, draws, losses = self._calculate_wdl(euro_fixtures)
        matches = len(euro_fixtures)
        points = wins * 3 + draws
        ppg = safe_divide(points, matches)
        win_pct = safe_divide(wins * 100, matches)

        gf = sum(self._goals_for(f) for f in euro_fixtures)
        ga = sum(self._goals_against(f) for f in euro_fixtures)
        gd = gf - ga
        gd_str = f"+{gd}" if gd > 0 else str(gd)

        print(
            f"Record: {wins}W - {draws}D - {losses}L ({win_pct:.1f}% win rate) | "
            f"{points} pts ({ppg:.2f} PPG)"
        )
        print(
            f"Goals:  {gf} for ({safe_divide(gf, matches):.2f}/gm) | "
            f"{ga} against ({safe_divide(ga, matches):.2f}/gm) | {gd_str} GD"
        )
        print()

        self._print_stats_table(euro_fixtures, label=euro_label)
        self._print_top_performers()

        # Domestic context block
        if domestic_fixtures:
            self._print_domestic_context(domestic_fixtures)
        else:
            print("── DOMESTIC CONTEXT ─────────────────────────────────────────────────────────")
            print("  No domestic league data available in system.")
            print()

    def _print_stats_table(self, fixtures: List[Dict], label: str = ""):
        print(f"TEAM STATS - {label.upper()}")
        print("-" * 80)
        print(f"{'STAT':<20} {'AVG/GM':>8} {'MIN':>6} {'MAX':>6}")
        print("-" * 80)

        stats = self._calculate_stat_ranges(fixtures)

        rows = [
            ("Goals Scored",    'gf'),
            ("Goals Conceded",  'ga'),
            ("Shots",           'shots'),
            ("Shots on Target", 'sot'),
            ("Corners",         'corners'),
            ("Cards",           'cards'),
            ("Offsides",        'offsides'),
            ("Fouls",           'fouls'),
            ("Possession %",    'poss'),
        ]

        for label_str, key in rows:
            avg = stats.get(f'{key}_avg', 0)
            mn  = stats.get(f'{key}_min', 0)
            mx  = stats.get(f'{key}_max', 0)
            print(f"{label_str:<20} {avg:>8.1f} {mn:>6.0f} {mx:>6.0f}")

        print()

    def _print_domestic_context(self, domestic_fixtures: List[Dict]):
        print("── DOMESTIC CONTEXT ─────────────────────────────────────────────────────────")
        print("  (Teams often rotate domestically during European campaigns)")
        print()

        matches = len(domestic_fixtures)
        if matches == 0:
            print("  No completed domestic fixtures found.")
            print()
            return

        wins, draws, losses = self._calculate_wdl(domestic_fixtures)
        points = wins * 3 + draws
        ppg = safe_divide(points, matches)
        gf = sum(self._goals_for(f) for f in domestic_fixtures)
        ga = sum(self._goals_against(f) for f in domestic_fixtures)

        shots_avg = safe_divide(
            sum(self._team_stat(f, 'shots') for f in domestic_fixtures), matches
        )
        sot_avg = safe_divide(
            sum(self._team_stat(f, 'sot') for f in domestic_fixtures), matches
        )
        cards_avg = safe_divide(
            sum(self._team_stat(f, 'cards') for f in domestic_fixtures), matches
        )

        print(
            f"  Domestic:  {wins}W-{draws}D-{losses}L | {ppg:.2f} PPG | "
            f"{safe_divide(gf, matches):.2f} GF | {safe_divide(ga, matches):.2f} GA"
        )
        print(
            f"  Shooting:  {shots_avg:.1f} shots/gm | {sot_avg:.1f} SOT/gm"
        )
        print(f"  Discipline: {cards_avg:.1f} cards/gm")
        print()

    def _print_top_performers(self):
        print("TOP PERFORMERS (European)")
        print("-" * 80)

        scorers = sorted(
            [p for p in self.players if p.get('goals_overall', 0) > 0
             and p.get('minutes_played_overall', 0) >= 90],
            key=lambda p: p.get('goals_overall', 0),
            reverse=True
        )
        assisters = sorted(
            [p for p in self.players if p.get('assists_overall', 0) > 0
             and p.get('minutes_played_overall', 0) >= 90],
            key=lambda p: p.get('assists_overall', 0),
            reverse=True
        )

        print("Goals:")
        if scorers:
            for i, p in enumerate(scorers[:3], 1):
                name = p.get('known_as', p.get('full_name', 'Unknown'))
                mins = p.get('minutes_played_overall', 0)
                goals = p.get('goals_overall', 0)
                per90 = safe_divide(goals * 90, mins)
                print(f"  {i}. {name:<25} {goals} goals ({per90:.2f}/90)")
        else:
            print("  None recorded")

        print("Assists:")
        if assisters:
            for i, p in enumerate(assisters[:3], 1):
                name = p.get('known_as', p.get('full_name', 'Unknown'))
                mins = p.get('minutes_played_overall', 0)
                assists = p.get('assists_overall', 0)
                per90 = safe_divide(assists * 90, mins)
                print(f"  {i}. {name:<25} {assists} assists ({per90:.2f}/90)")
        else:
            print("  None recorded")
        print()

    # ── helpers ──────────────────────────────────────────────────────────────

    def _goals_for(self, fixture: Dict) -> int:
        is_home = fixture.get('homeID') == self.team_id
        return fixture.get('homeGoalCount', 0) if is_home else fixture.get('awayGoalCount', 0)

    def _goals_against(self, fixture: Dict) -> int:
        is_home = fixture.get('homeID') == self.team_id
        return fixture.get('awayGoalCount', 0) if is_home else fixture.get('homeGoalCount', 0)

    def _team_stat(self, fixture: Dict, stat: str) -> float:
        is_home = fixture.get('homeID') == self.team_id
        prefix = 'team_a' if is_home else 'team_b'
        mapping = {
            'shots':    f'{prefix}_shots',
            'sot':      f'{prefix}_shotsOnTarget',
            'corners':  f'{prefix}_corners',
            'cards':    f'{prefix}_cards_num',
            'offsides': f'{prefix}_offsides',
            'fouls':    f'{prefix}_fouls',
            'poss':     f'{prefix}_possession',
        }
        val = fixture.get(mapping.get(stat, ''), 0)
        return val if val >= 0 else 0

    def _calculate_wdl(self, fixtures: List[Dict]):
        wins = draws = losses = 0
        for f in fixtures:
            gf = self._goals_for(f)
            ga = self._goals_against(f)
            if gf > ga:
                wins += 1
            elif gf < ga:
                losses += 1
            else:
                draws += 1
        return wins, draws, losses

    def _calculate_stat_ranges(self, fixtures: List[Dict]) -> Dict:
        keys = ['gf', 'ga', 'shots', 'sot', 'corners', 'cards', 'offsides', 'fouls', 'poss']
        data = {k: [] for k in keys}

        for f in fixtures:
            data['gf'].append(self._goals_for(f))
            data['ga'].append(self._goals_against(f))
            for k in ['shots', 'sot', 'corners', 'cards', 'offsides', 'fouls', 'poss']:
                data[k].append(self._team_stat(f, k))

        result = {}
        for k in keys:
            vals = [v for v in data[k] if v >= 0]
            result[f'{k}_avg'] = safe_divide(sum(vals), len(vals))
            result[f'{k}_min'] = min(vals) if vals else 0
            result[f'{k}_max'] = max(vals) if vals else 0
        return result