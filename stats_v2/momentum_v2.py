"""
Momentum Analyzer V2 - Enhanced with shooting and discipline trends
"""

from typing import List, Dict, Optional
from betting.utils import safe_divide


EUROPEAN_KEYS = {'champions_league', 'europa_league', 'europa_conference_league'}


class MomentumAnalyzerV2:
    """Enhanced momentum analysis"""

    def __init__(self, recent_fixtures: List[Dict], team_id: int,
                 season_avg_goals_for: float, season_avg_goals_against: float,
                 season_avg_shots: float, season_avg_sot: float,
                 season_avg_cards: float, season_avg_corners: float,
                 season_avg_fouls: float,
                 euro_fixtures: Optional[List[Dict]] = None):
        self.fixtures = recent_fixtures
        self.team_id = team_id
        self.season_avg_gf = season_avg_goals_for
        self.season_avg_ga = season_avg_goals_against
        self.season_avg_shots = season_avg_shots
        self.season_avg_sot = season_avg_sot
        self.season_avg_cards = season_avg_cards
        self.season_avg_corners = season_avg_corners
        self.season_avg_fouls = season_avg_fouls
        self.euro_fixtures = euro_fixtures or []

    def print_momentum(self):
        print("=" * 80)
        print("📈 MOMENTUM ANALYSIS")
        print("=" * 80)
        print()

        last_3_ppg  = self._calculate_ppg(self.fixtures[-3:])
        last_5_ppg  = self._calculate_ppg(self.fixtures[-5:])
        last_10_ppg = self._calculate_ppg(self.fixtures[-10:])

        print("Performance Trend:")
        print(f"  Last 3:  {last_3_ppg:.2f} PPG {self._get_momentum_emoji(last_3_ppg)}  |  "
              f"Last 5:  {last_5_ppg:.2f} PPG {self._get_momentum_emoji(last_5_ppg)}  |  "
              f"Last 10: {last_10_ppg:.2f} PPG {self._get_momentum_emoji(last_10_ppg)}")
        print()

        last_10_gf = self._calculate_avg_goals_for(self.fixtures[-10:])
        last_10_ga = self._calculate_avg_goals_against(self.fixtures[-10:])

        attack_trend  = "↗️ " if last_10_gf > self.season_avg_gf else "↘️ " if last_10_gf < self.season_avg_gf else "→ "
        attack_status = "IMPROVING" if last_10_gf > self.season_avg_gf else "DECLINING" if last_10_gf < self.season_avg_gf else "STABLE"
        print(f"Attack:   {last_10_gf:.1f} goals/gm ({attack_trend}vs {self.season_avg_gf:.2f} season avg) {attack_status}")

        defense_trend  = "↗️ " if last_10_ga < self.season_avg_ga else "↘️ " if last_10_ga > self.season_avg_ga else "→ "
        defense_status = "TIGHTENING" if last_10_ga < self.season_avg_ga else "LEAKING" if last_10_ga > self.season_avg_ga else "STABLE"
        print(f"Defense:  {last_10_ga:.1f} goals/gm ({defense_trend}vs {self.season_avg_ga:.2f} season avg) {defense_status}")
        print()

        last_10_shots = self._calculate_avg_stat(self.fixtures[-10:], 'shots')
        last_10_sot   = self._calculate_avg_stat(self.fixtures[-10:], 'sot')

        shots_trend = "↗️ " if last_10_shots > self.season_avg_shots else "↘️ " if last_10_shots < self.season_avg_shots else "→ "
        sot_trend   = "↗️ " if last_10_sot > self.season_avg_sot else "↘️ " if last_10_sot < self.season_avg_sot else "→ "

        shot_accuracy_last10 = safe_divide(last_10_sot * 100, last_10_shots)
        shot_accuracy_season = safe_divide(self.season_avg_sot * 100, self.season_avg_shots)

        print("Shooting:")
        print(f"  Last 10: {last_10_shots:.1f} shots/gm ({shots_trend}vs {self.season_avg_shots:.1f} season avg)")
        print(f"  Last 10: {last_10_sot:.1f} SOT/gm ({sot_trend}vs {self.season_avg_sot:.1f} season avg)")
        print(f"  Accuracy: {shot_accuracy_last10:.1f}% (Last 10) vs {shot_accuracy_season:.1f}% (Season)")
        print()

        last_10_cards = self._calculate_avg_stat(self.fixtures[-10:], 'cards')
        cards_trend = "↗️ IMPROVING" if last_10_cards < self.season_avg_cards else "↘️ WORSENING" if last_10_cards > self.season_avg_cards else "→ STABLE"
        print("Discipline:")
        print(f"  Last 10: {last_10_cards:.1f} cards/gm ({cards_trend} vs {self.season_avg_cards:.1f} season avg)")
        print()

        home_form = self._get_venue_form(home=True)
        away_form = self._get_venue_form(home=False)
        print("Venue Split:")
        print(f"  Home (last 5):  {home_form}")
        print(f"  Away (last 5):  {away_form}")
        print()

        print("Key Trends:")
        if last_10_shots > self.season_avg_shots:
            print(f"  ✓ Shooting volume increasing ({last_10_shots:.1f} vs {self.season_avg_shots:.1f})")
        corners_last10 = self._calculate_avg_stat(self.fixtures[-10:], 'corners')
        if corners_last10 > self.season_avg_corners:
            print(f"  ✓ Creating more corners ({corners_last10:.1f} vs {self.season_avg_corners:.1f})")
        fouls_last10 = self._calculate_avg_stat(self.fixtures[-10:], 'fouls')
        if fouls_last10 < self.season_avg_fouls:
            print(f"  ✓ Fewer fouls conceded ({fouls_last10:.1f} vs {self.season_avg_fouls:.1f})")
        if shot_accuracy_last10 < shot_accuracy_season:
            print(f"  ⚠️ Shot accuracy down ({shot_accuracy_last10:.1f}% vs {shot_accuracy_season:.1f}%)")
        print()

        momentum_rating = self._calculate_momentum_rating(last_5_ppg)
        trend = "↗️ RISING" if last_5_ppg > last_10_ppg else "↘️ FALLING" if last_5_ppg < last_10_ppg else "→ STABLE"
        print(f"Overall Momentum: {momentum_rating}/100 {self._get_stars(momentum_rating)} | Trend: {trend}")
        print()

        # European vs domestic comparison — only shown if euro fixtures exist
        if self.euro_fixtures:
            self._print_euro_vs_domestic()

    def _print_euro_vs_domestic(self):
        """Compare performance in European vs domestic fixtures."""
        dom_fixtures  = [f for f in self.fixtures if f.get('_league_key', '') not in EUROPEAN_KEYS]
        euro_fixtures = self.euro_fixtures

        print("── EUROPEAN vs DOMESTIC FORM ────────────────────────────────────────────────")
        print()
        print(f"  {'':30} {'European':^20}  {'Domestic':^20}")
        print("  " + "-" * 72)

        def block_stats(fixtures):
            if not fixtures:
                return None
            n = len(fixtures)
            ppg = self._calculate_ppg(fixtures)
            gf  = self._calculate_avg_goals_for(fixtures)
            ga  = self._calculate_avg_goals_against(fixtures)
            shots = self._calculate_avg_stat(fixtures, 'shots')
            sot   = self._calculate_avg_stat(fixtures, 'sot')
            cards = self._calculate_avg_stat(fixtures, 'cards')
            return {'n': n, 'ppg': ppg, 'gf': gf, 'ga': ga,
                    'shots': shots, 'sot': sot, 'cards': cards}

        es = block_stats(euro_fixtures)
        ds = block_stats(dom_fixtures)

        def row(label, ekey, dkey=None, fmt='.2f'):
            dkey = dkey or ekey
            ev = format(es[ekey], fmt) if es else 'N/A'
            dv = format(ds[dkey], fmt) if ds else 'N/A'
            print(f"  {label:<30} {ev:^20}  {dv:^20}")

        row("Matches",       'n',     fmt='d')
        row("PPG",           'ppg')
        row("Goals For/gm",  'gf')
        row("Goals Agn/gm",  'ga')
        row("Shots/gm",      'shots', fmt='.1f')
        row("SOT/gm",        'sot',   fmt='.1f')
        row("Cards/gm",      'cards', fmt='.1f')
        print()
        print("  Note: Different form in different competitions is normal —")
        print("  managers rotate squads and set up differently for Europe.")
        print()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _calculate_ppg(self, fixtures: List[Dict]) -> float:
        if not fixtures:
            return 0.0
        points = 0
        for f in fixtures:
            is_home = f.get('homeID') == self.team_id
            hg = f.get('homeGoalCount', 0)
            ag = f.get('awayGoalCount', 0)
            if is_home:
                if hg > ag: points += 3
                elif hg == ag: points += 1
            else:
                if ag > hg: points += 3
                elif ag == hg: points += 1
        return points / len(fixtures)

    def _calculate_avg_goals_for(self, fixtures: List[Dict]) -> float:
        if not fixtures:
            return 0.0
        goals = sum(
            f.get('homeGoalCount', 0) if f.get('homeID') == self.team_id else f.get('awayGoalCount', 0)
            for f in fixtures
        )
        return goals / len(fixtures)

    def _calculate_avg_goals_against(self, fixtures: List[Dict]) -> float:
        if not fixtures:
            return 0.0
        goals = sum(
            f.get('awayGoalCount', 0) if f.get('homeID') == self.team_id else f.get('homeGoalCount', 0)
            for f in fixtures
        )
        return goals / len(fixtures)

    def _calculate_avg_stat(self, fixtures: List[Dict], stat_type: str) -> float:
        if not fixtures:
            return 0.0
        mapping = {
            'shots':   ('team_a_shots',         'team_b_shots'),
            'sot':     ('team_a_shotsOnTarget',  'team_b_shotsOnTarget'),
            'cards':   ('team_a_cards_num',      'team_b_cards_num'),
            'corners': ('team_a_corners',        'team_b_corners'),
            'fouls':   ('team_a_fouls',          'team_b_fouls'),
        }
        home_key, away_key = mapping.get(stat_type, ('', ''))
        values = []
        for f in fixtures:
            is_home = f.get('homeID') == self.team_id
            val = f.get(home_key if is_home else away_key, 0)
            if val >= 0:
                values.append(val)
        return safe_divide(sum(values), len(values))

    def _get_venue_form(self, home: bool) -> str:
        key = 'homeID' if home else 'awayID'
        fixtures = [f for f in self.fixtures[-5:] if f.get(key) == self.team_id]
        if not fixtures:
            return "N/A"
        w = d = l = 0
        gf = ga = 0
        for f in fixtures:
            hg = f.get('homeGoalCount', 0)
            ag = f.get('awayGoalCount', 0)
            team_gf = hg if home else ag
            team_ga = ag if home else hg
            gf += team_gf
            ga += team_ga
            if team_gf > team_ga: w += 1
            elif team_gf < team_ga: l += 1
            else: d += 1
        ppg = self._calculate_ppg(fixtures)
        if ppg >= 2.5:   label = "⚡⚡⚡ EXCELLENT"
        elif ppg >= 2.0: label = "⚡⚡ STRONG"
        elif ppg >= 1.5: label = "⚡ GOOD"
        else:            label = "⚠️ MIXED"
        return f"{label}  |  {w}W-{d}D-{l}L  |  {gf} GF, {ga} GA"

    def _calculate_momentum_rating(self, ppg: float) -> int:
        return min(100, int(ppg * 40))

    def _get_momentum_emoji(self, ppg: float) -> str:
        if ppg >= 2.5:   return "⚡⚡⚡"
        elif ppg >= 2.0: return "⚡⚡"
        elif ppg >= 1.5: return "⚡"
        else:            return "⚠️"

    def _get_stars(self, rating: int) -> str:
        if rating >= 90:   return "⚡⚡⚡⚡⚡ ELITE"
        elif rating >= 80: return "⚡⚡⚡⚡ VERY STRONG"
        elif rating >= 70: return "⚡⚡⚡ STRONG"
        elif rating >= 60: return "⚡⚡ GOOD"
        else:              return "⚡ AVERAGE"