"""
Fixture Analysis - Knockout head-to-head output for two teams in a specific fixture
"""

from typing import Dict, List, Optional
from betting.utils import safe_divide, format_date


EUROPEAN_KEYS = {'champions_league', 'europa_league', 'europa_conference_league'}

COMP_TAGS = {
    'champions_league':         '[UCL]',
    'europa_league':            '[UEL]',
    'europa_conference_league': '[UECL]',
}


class FixtureAnalysis:
    """
    Head-to-head analysis for a specific knockout fixture.
    Each team shown sequentially: all European matches this season,
    summary, last 5 league games, then domestic context.
    """

    def __init__(self, loader, calculator):
        self.loader = loader
        self.calculator = calculator

    def print_fixture_analysis(
        self,
        fixture: Dict,
        euro_key: str,
        euro_season_id: int,
        all_fixtures_home: List[Dict],
        all_fixtures_away: List[Dict],
    ):
        home_id      = fixture.get('homeID')
        away_id      = fixture.get('awayID')
        home_name    = fixture.get('home_name', 'Home Team')
        away_name    = fixture.get('away_name', 'Away Team')
        date         = format_date(fixture.get('date_unix', 0))
        no_home_away = fixture.get('no_home_away', 0)
        venue_note   = " (Neutral Venue)" if no_home_away else ""

        print("=" * 80)
        print(f"⚽ KNOCKOUT FIXTURE ANALYSIS{venue_note}")
        print(f"   {home_name} vs {away_name}  —  {date}")
        print("=" * 80)

        for team_id, team_name, all_fixtures in [
            (home_id, home_name, all_fixtures_home),
            (away_id, away_name, all_fixtures_away),
        ]:
            self._print_team_section(
                team_id, team_name, all_fixtures,
                euro_key, euro_season_id,
            )

    # ── team section ──────────────────────────────────────────────────────────

    def _print_team_section(
        self,
        team_id: int,
        team_name: str,
        all_fixtures: List[Dict],
        euro_key: str,
        euro_season_id: int,
    ):
        print()
        print("=" * 80)
        print(f"  {team_name.upper()}")
        print("=" * 80)
        print()

        euro_fixtures = sorted(
            [f for f in all_fixtures
             if f.get('_league_key') == euro_key and f.get('status') == 'complete'],
            key=lambda f: f.get('date_unix', 0)
        )

        domestic_fixtures = sorted(
            [f for f in all_fixtures
             if f.get('_league_key') not in EUROPEAN_KEYS and f.get('status') == 'complete'],
            key=lambda f: f.get('date_unix', 0)
        )

        # Players — try domestic first, fall back to euro
        players = []
        if domestic_fixtures:
            dom_key = domestic_fixtures[0].get('_league_key')
            dom_sid = domestic_fixtures[0].get('_season_id')
            if dom_key and dom_sid:
                players = self.loader.load_team_players(dom_key, dom_sid, team_id) or []
        if not players:
            players = self.loader.load_team_players(euro_key, euro_season_id, team_id) or []

        # Collect opponent players for name lookup
        all_players = list(players)
        seen_tids = {team_id}
        for f in euro_fixtures:
            for id_key in ['homeID', 'awayID']:
                tid = f.get(id_key)
                if tid and tid not in seen_tids:
                    seen_tids.add(tid)
                    tp = self.loader.load_team_players(euro_key, euro_season_id, tid)
                    if not tp and domestic_fixtures:
                        dom_key = domestic_fixtures[0].get('_league_key')
                        dom_sid = domestic_fixtures[0].get('_season_id')
                        if dom_key and dom_sid:
                            tp = self.loader.load_team_players(dom_key, dom_sid, tid)
                    if tp:
                        all_players.extend(tp)

        if not euro_fixtures:
            print(f"  No completed European fixtures found for {team_name}.")
            print()
            return

        # 1. European season header
        self._print_euro_header(team_id, euro_fixtures, euro_key)

        # 2. All European matches listed match-by-match
        print("📋 ALL EUROPEAN MATCHES THIS SEASON")
        print("=" * 80)
        print()

        for idx, fixture in enumerate(euro_fixtures, 1):
            match_id = fixture.get('id')
            fkey     = fixture.get('_league_key', euro_key)
            fsid     = fixture.get('_season_id', euro_season_id)
            detail   = self.loader.load_match_details(fkey, fsid, match_id)
            if detail:
                detail['_league_key'] = fkey
                self._print_single_match(detail, team_id, team_name, idx, all_players)
                print("-" * 80)
                print()

        # 3. European summary
        self._print_euro_summary(team_id, euro_fixtures, all_players, euro_key, euro_season_id)

        # 4. Last 5 league games (if domestic data available)
        if domestic_fixtures:
            self._print_last_5_league(
                team_id, team_name, domestic_fixtures, all_players,
                domestic_fixtures[0].get('_league_key', ''),
                domestic_fixtures[0].get('_season_id', 0),
            )

        # 5. Domestic context summary
        self._print_domestic_context(team_id, domestic_fixtures)

    # ── section printers ──────────────────────────────────────────────────────

    def _print_euro_header(self, team_id: int, euro_fixtures: List[Dict], euro_key: str):
        n    = len(euro_fixtures)
        wins, draws, losses = self._wdl(euro_fixtures, team_id)
        pts  = wins * 3 + draws
        ppg  = safe_divide(pts, n)
        gf   = sum(self._goals_for(f, team_id) for f in euro_fixtures)
        ga   = sum(self._goals_against(f, team_id) for f in euro_fixtures)
        comp = euro_key.replace('_', ' ').title()

        print(f"📊 {comp.upper()} SEASON ({n} matches)")
        print("-" * 80)
        print(f"Record: {wins}W - {draws}D - {losses}L | {ppg:.2f} PPG")
        print(f"Goals:  {gf} for ({safe_divide(gf, n):.2f}/gm) | "
              f"{ga} against ({safe_divide(ga, n):.2f}/gm)")
        print()

    def _print_single_match(self, match: Dict, team_id: int, team_name: str,
                             match_num: int, all_players: List[Dict]):
        home_name  = match.get('home_name', 'Unknown')
        away_name  = match.get('away_name', 'Unknown')
        home_goals = match.get('homeGoalCount', 0)
        away_goals = match.get('awayGoalCount', 0)
        date       = format_date(match.get('date_unix', 0))
        comp_tag   = COMP_TAGS.get(match.get('_league_key', ''), '')
        is_home    = match.get('homeID') == team_id

        result = ("WIN" if (is_home and home_goals > away_goals) or (not is_home and away_goals > home_goals)
                  else "LOSS" if (is_home and home_goals < away_goals) or (not is_home and away_goals < home_goals)
                  else "DRAW")

        tag_str = f" {comp_tag}" if comp_tag else ""
        print(f"Match {match_num}: {home_name} {home_goals}-{away_goals} {away_name} "
              f"({date}){tag_str} - {result}")
        print("-" * 80)

        h_corners  = max(match.get('team_a_corners', 0), 0)
        a_corners  = max(match.get('team_b_corners', 0), 0)
        h_shots    = max(match.get('team_a_shots', 0), 0)
        a_shots    = max(match.get('team_b_shots', 0), 0)
        h_sot      = max(match.get('team_a_shotsOnTarget', 0), 0)
        a_sot      = max(match.get('team_b_shotsOnTarget', 0), 0)
        h_cards    = max(match.get('team_a_cards_num', 0), 0)
        a_cards    = max(match.get('team_b_cards_num', 0), 0)
        h_offsides = max(match.get('team_a_offsides', 0), 0)
        a_offsides = max(match.get('team_b_offsides', 0), 0)
        h_fouls    = max(match.get('team_a_fouls', 0), 0)
        a_fouls    = max(match.get('team_b_fouls', 0), 0)
        h_poss     = max(match.get('team_a_possession', 0), 0)
        a_poss     = max(match.get('team_b_possession', 0), 0)

        print(f"{'TEAM STATS':<25} {home_name[:15]:>15}  {away_name[:15]:>15}  {'Match Total':>15}")
        print(f"{'Corners':<25} {h_corners:>15}  {a_corners:>15}  {h_corners + a_corners:>15}")
        print(f"{'Shots':<25} {h_shots:>15}  {a_shots:>15}  {h_shots + a_shots:>15}")
        print(f"{'Shots on Target':<25} {h_sot:>15}  {a_sot:>15}  {h_sot + a_sot:>15}")
        print(f"{'Cards':<25} {h_cards:>15}  {a_cards:>15}  {h_cards + a_cards:>15}")
        print(f"{'Offsides':<25} {h_offsides:>15}  {a_offsides:>15}  {h_offsides + a_offsides:>15}")
        print(f"{'Fouls':<25} {h_fouls:>15}  {a_fouls:>15}  {h_fouls + a_fouls:>15}")
        print(f"{'Possession %':<25} {h_poss:>15}  {a_poss:>15}  {100:>15}")
        print()

        prefix_for = 'team_a' if is_home else 'team_b'
        print(f"PLAYER STATS - {team_name.upper()}")

        goals_list = match.get(f'{prefix_for}_goal_details', [])
        if goals_list:
            goal_scorers = []
            for goal in goals_list:
                pid   = goal.get('player_id')
                pname = self._get_player_name(pid, all_players) if pid else "Unknown"
                time  = goal.get('time', '?')
                goal_scorers.append(f"{pname} ({time}')")
            print(f"Goals:      {', '.join(goal_scorers)}")
        else:
            print(f"Goals:      None")

        if goals_list:
            assist_providers = []
            for goal in goals_list:
                aid = goal.get('assist_player_id', -1)
                if aid and aid != -1:
                    aname = self._get_player_name(aid, all_players)
                    if aname not in assist_providers and aname != "Unknown":
                        assist_providers.append(aname)
            print(f"Assists:    {', '.join(assist_providers) if assist_providers else 'None'}")

        cards_list = match.get(f'{prefix_for}_card_details', [])
        if cards_list:
            card_players = []
            for card in cards_list:
                if card.get('card_type') in ['Yellow', 'Second Yellow', 'Red']:
                    pid   = card.get('player_id')
                    pname = self._get_player_name(pid, all_players) if pid else "Unknown"
                    ctype = card.get('card_type', 'Yellow')
                    time  = card.get('time', '?')
                    card_players.append(f"{pname} ({ctype} {time}')")
            print(f"Cards:      {', '.join(card_players) if card_players else 'None'}")
        else:
            print(f"Cards:      None")

    def _print_euro_summary(self, team_id: int, euro_fixtures: List[Dict],
                             all_players: List[Dict], euro_key: str, euro_season_id: int):
        n = len(euro_fixtures)
        wins = draws = losses = 0
        gf = ga = 0
        corners_for = []; shots_for = []; sot_for = []
        cards_for = []; offsides_for = []; fouls_for = []
        corners_against = []; shots_against = []; sot_against = []
        cards_against = []; offsides_against = []; fouls_against = []
        player_goals = {}; player_assists = {}; player_cards = {}

        for f in euro_fixtures:
            is_home  = f.get('homeID') == team_id
            team_gf  = self._goals_for(f, team_id)
            team_ga  = self._goals_against(f, team_id)
            gf += team_gf
            ga += team_ga
            if team_gf > team_ga:   wins += 1
            elif team_gf < team_ga: losses += 1
            else:                   draws += 1

            pfor = 'team_a' if is_home else 'team_b'
            pagn = 'team_b' if is_home else 'team_a'

            def _s(val): return max(val, 0)
            corners_for.append(_s(f.get(f'{pfor}_corners', 0)))
            corners_against.append(_s(f.get(f'{pagn}_corners', 0)))
            shots_for.append(_s(f.get(f'{pfor}_shots', 0)))
            shots_against.append(_s(f.get(f'{pagn}_shots', 0)))
            sot_for.append(_s(f.get(f'{pfor}_shotsOnTarget', 0)))
            sot_against.append(_s(f.get(f'{pagn}_shotsOnTarget', 0)))
            cards_for.append(_s(f.get(f'{pfor}_cards_num', 0)))
            cards_against.append(_s(f.get(f'{pagn}_cards_num', 0)))
            offsides_for.append(_s(f.get(f'{pfor}_offsides', 0)))
            offsides_against.append(_s(f.get(f'{pagn}_offsides', 0)))
            fouls_for.append(_s(f.get(f'{pfor}_fouls', 0)))
            fouls_against.append(_s(f.get(f'{pagn}_fouls', 0)))

            match_id = f.get('id')
            fkey     = f.get('_league_key', euro_key)
            fsid     = f.get('_season_id', euro_season_id)
            detail   = self.loader.load_match_details(fkey, fsid, match_id)
            if detail:
                for goal in detail.get(f'{pfor}_goal_details', []):
                    pid = goal.get('player_id')
                    if pid:
                        pname = self._get_player_name(pid, all_players)
                        player_goals[pname] = player_goals.get(pname, 0) + 1
                    aid = goal.get('assist_player_id', -1)
                    if aid and aid != -1:
                        aname = self._get_player_name(aid, all_players)
                        player_assists[aname] = player_assists.get(aname, 0) + 1
                for card in detail.get(f'{pfor}_card_details', []):
                    if card.get('card_type') in ['Yellow', 'Second Yellow', 'Red']:
                        pid = card.get('player_id')
                        if pid:
                            pname = self._get_player_name(pid, all_players)
                            player_cards[pname] = player_cards.get(pname, 0) + 1

        pts = wins * 3 + draws

        def avg(lst): return safe_divide(sum(lst), len(lst)) if lst else 0

        print(f"EUROPEAN SUMMARY ({n} matches)")
        print("-" * 80)
        print(f"Record:       {wins}W - {draws}D - {losses}L ({pts} points from {n * 3})")
        print(f"Goals:        {gf} scored ({safe_divide(gf, n):.1f}/gm) | "
              f"{ga} conceded ({safe_divide(ga, n):.1f}/gm)")
        print()
        print("TEAM AVERAGES")
        print(f"  Corners:    {avg(corners_for):.1f} per game (opponents: {avg(corners_against):.1f})")
        print(f"  Shots:      {avg(shots_for):.1f} per game (opponents: {avg(shots_against):.1f})")
        print(f"  SOT:        {avg(sot_for):.1f} per game (opponents: {avg(sot_against):.1f})")
        print(f"  Cards:      {avg(cards_for):.1f} per game (opponents: {avg(cards_against):.1f})")
        print(f"  Offsides:   {avg(offsides_for):.1f} per game (opponents: {avg(offsides_against):.1f})")
        print(f"  Fouls:      {avg(fouls_for):.1f} per game (opponents: {avg(fouls_against):.1f})")
        print()
        print("PLAYER STATS (European)")
        if player_goals:
            top = max(player_goals.items(), key=lambda x: x[1])
            print(f"  Top Scorer:     {top[0]} ({top[1]} goals)")
        else:
            print(f"  Top Scorer:     None")
        if player_assists:
            top = max(player_assists.items(), key=lambda x: x[1])
            print(f"  Top Assister:   {top[0]} ({top[1]} assists)")
        else:
            print(f"  Top Assister:   None")
        if player_cards:
            top = max(player_cards.items(), key=lambda x: x[1])
            risk = "⚠️  RISK" if top[1] >= 3 else ""
            print(f"  Most Carded:    {top[0]} ({top[1]} cards) {risk}")
        else:
            print(f"  Most Carded:    None")
        print()

    def _print_last_5_league(self, team_id: int, team_name: str,
                              domestic_fixtures: List[Dict], all_players: List[Dict],
                              dom_key: str, dom_sid: int):
        last_5 = domestic_fixtures[-5:]
        dom_label = dom_key.replace('_', ' ').title()

        print(f"── LAST 5 {dom_label.upper()} MATCHES ────────────────────────────────────────")
        print()

        for idx, fixture in enumerate(last_5, 1):
            match_id = fixture.get('id')
            fkey     = fixture.get('_league_key', dom_key)
            fsid     = fixture.get('_season_id', dom_sid)
            detail   = self.loader.load_match_details(fkey, fsid, match_id)
            if detail:
                detail['_league_key'] = fkey
                self._print_single_match(detail, team_id, team_name, idx, all_players)
                print("-" * 80)
                print()

    def _print_domestic_context(self, team_id: int, domestic_fixtures: List[Dict]):
        print("── DOMESTIC CONTEXT ─────────────────────────────────────────────────────────")
        print()

        if not domestic_fixtures:
            print("  No domestic league data available in system.")
            print()
            return

        n    = len(domestic_fixtures)
        wins, draws, losses = self._wdl(domestic_fixtures, team_id)
        pts  = wins * 3 + draws
        ppg  = safe_divide(pts, n)
        gf   = sum(self._goals_for(f, team_id) for f in domestic_fixtures)
        ga   = sum(self._goals_against(f, team_id) for f in domestic_fixtures)

        shots_vals = []
        sot_vals   = []
        cards_vals = []
        for f in domestic_fixtures:
            is_home = f.get('homeID') == team_id
            prefix  = 'team_a' if is_home else 'team_b'
            s  = f.get(f'{prefix}_shots', 0)
            st = f.get(f'{prefix}_shotsOnTarget', 0)
            c  = f.get(f'{prefix}_cards_num', 0)
            if s  >= 0: shots_vals.append(s)
            if st >= 0: sot_vals.append(st)
            if c  >= 0: cards_vals.append(c)

        dom_key   = domestic_fixtures[0].get('_league_key', '')
        dom_label = dom_key.replace('_', ' ').title()

        print(f"  {dom_label} ({n} matches)")
        print(f"  Record:     {wins}W - {draws}D - {losses}L | {ppg:.2f} PPG")
        print(f"  Goals:      {safe_divide(gf, n):.2f} scored/gm | "
              f"{safe_divide(ga, n):.2f} conceded/gm")
        if shots_vals:
            print(f"  Shooting:   {safe_divide(sum(shots_vals), len(shots_vals)):.1f} shots/gm | "
                  f"{safe_divide(sum(sot_vals), len(sot_vals)):.1f} SOT/gm")
        if cards_vals:
            print(f"  Discipline: {safe_divide(sum(cards_vals), len(cards_vals)):.1f} cards/gm")
        print()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _goals_for(self, fixture: Dict, team_id: int) -> int:
        is_home = fixture.get('homeID') == team_id
        return fixture.get('homeGoalCount', 0) if is_home else fixture.get('awayGoalCount', 0)

    def _goals_against(self, fixture: Dict, team_id: int) -> int:
        is_home = fixture.get('homeID') == team_id
        return fixture.get('awayGoalCount', 0) if is_home else fixture.get('homeGoalCount', 0)

    def _wdl(self, fixtures: List[Dict], team_id: int):
        wins = draws = losses = 0
        for f in fixtures:
            gf = self._goals_for(f, team_id)
            ga = self._goals_against(f, team_id)
            if gf > ga:   wins += 1
            elif gf < ga: losses += 1
            else:         draws += 1
        return wins, draws, losses

    def _get_player_name(self, player_id: int, players: List[Dict]) -> str:
        if not player_id or not players:
            return "Unknown"
        for p in players:
            if p.get('id') == player_id:
                return p.get('known_as', p.get('full_name', 'Unknown'))
        return "Unknown"