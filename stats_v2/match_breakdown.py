"""
Match Breakdown - Detailed last 10 matches with player stats
"""

from typing import List, Dict, Optional
from betting.utils import format_date, safe_divide


EUROPEAN_KEYS = {'champions_league', 'europa_league', 'europa_conference_league'}

COMP_TAGS = {
    'champions_league': '[UCL]',
    'europa_league':    '[UEL]',
    'europa_conference_league':'[UECL]',
}


class MatchBreakdown:
    """Detailed breakdown of last N matches"""

    def __init__(self, team_id: int, team_name: str, all_players: List[Dict]):
        self.team_id = team_id
        self.team_name = team_name
        self.all_players = all_players

    def print_last_n_breakdown(self, match_details: List[Dict], n: int = 10):
        """
        Print detailed breakdown of last N matches.
        match_details may contain a mix of domestic and European fixtures.
        Each fixture is tagged with its competition.
        """
        print("=" * 80)
        print(f"📋 LAST {n} MATCHES - DETAILED BREAKDOWN (All Competitions)")
        print("=" * 80)
        print()

        if not match_details:
            print("No match data available")
            print()
            return

        for idx, match in enumerate(match_details, 1):
            self._print_single_match(match, idx)
            print("-" * 80)
            print()

        self._print_summary(match_details)

    def _get_player_name(self, player_id: int) -> str:
        if not self.all_players:
            return "Unknown"
        for player in self.all_players:
            if player.get('id') == player_id:
                return player.get('known_as', player.get('full_name', 'Unknown'))
        return "Unknown"

    def _comp_tag(self, match: Dict) -> str:
        """Return competition tag string for display."""
        league_key = match.get('_league_key', '')
        return COMP_TAGS.get(league_key, '')

    def _print_single_match(self, match: Dict, match_num: int):
        home_name  = match.get('home_name', 'Unknown')
        away_name  = match.get('away_name', 'Unknown')
        home_goals = match.get('homeGoalCount', 0)
        away_goals = match.get('awayGoalCount', 0)
        date       = format_date(match.get('date_unix', 0))
        comp_tag   = self._comp_tag(match)
        is_home    = match.get('homeID') == self.team_id

        if is_home:
            result = "WIN" if home_goals > away_goals else "LOSS" if home_goals < away_goals else "DRAW"
        else:
            result = "WIN" if away_goals > home_goals else "LOSS" if away_goals < home_goals else "DRAW"

        tag_str = f" {comp_tag}" if comp_tag else ""
        print(f"Match {match_num}: {home_name} {home_goals}-{away_goals} {away_name} ({date}){tag_str} - {result}")
        print("-" * 80)

        # Guard against incomplete match data (e.g. -1 fields on upcoming fixtures)
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

        print(f"PLAYER STATS - {self.team_name.upper()}")

        goals_list = match.get('team_a_goal_details', []) if is_home else match.get('team_b_goal_details', [])
        if goals_list:
            goal_scorers = []
            for goal in goals_list:
                player_id = goal.get('player_id')
                player_name = self._get_player_name(player_id) if player_id else "Unknown"
                time = goal.get('time', '?')
                goal_scorers.append(f"{player_name} ({time}')")
            print(f"Goals:      {', '.join(goal_scorers)}")
        else:
            print(f"Goals:      None")

        if goals_list:
            assist_providers = []
            for goal in goals_list:
                assist_id = goal.get('assist_player_id', -1)
                if assist_id and assist_id != -1:
                    assist_name = self._get_player_name(assist_id)
                    if assist_name not in assist_providers and assist_name != "Unknown":
                        assist_providers.append(assist_name)
            print(f"Assists:    {', '.join(assist_providers) if assist_providers else 'None'}")

        cards_list = match.get('team_a_card_details', []) if is_home else match.get('team_b_card_details', [])
        if cards_list:
            card_players = []
            for card in cards_list:
                if card.get('card_type') in ['Yellow', 'Second Yellow', 'Red']:
                    player_id = card.get('player_id')
                    player_name = self._get_player_name(player_id) if player_id else "Unknown"
                    card_type = card.get('card_type', 'Yellow')
                    time = card.get('time', '?')
                    card_players.append(f"{player_name} ({card_type} {time}')")
            print(f"Cards:      {', '.join(card_players) if card_players else 'None'}")
        else:
            print(f"Cards:      None")

    def _print_summary(self, match_details: List[Dict]):
        print("LAST {} SUMMARY".format(len(match_details)))
        print("-" * 80)

        wins = draws = losses = 0
        gf = ga = 0

        corners_for = []; corners_against = []
        shots_for = []; shots_against = []
        sot_for = []; sot_against = []
        cards_for = []; cards_against = []
        offsides_for = []; offsides_against = []
        fouls_for = []; fouls_against = []

        player_goals = {}
        player_assists = {}
        player_cards = {}

        # Track per-competition results for the summary line
        league_record = {'w': 0, 'd': 0, 'l': 0}
        euro_record   = {'w': 0, 'd': 0, 'l': 0}

        for match in match_details:
            is_home    = match.get('homeID') == self.team_id
            home_goals = match.get('homeGoalCount', 0)
            away_goals = match.get('awayGoalCount', 0)
            is_euro    = match.get('_league_key', '') in EUROPEAN_KEYS

            team_gf = home_goals if is_home else away_goals
            team_ga = away_goals if is_home else home_goals
            gf += team_gf
            ga += team_ga

            if team_gf > team_ga:
                wins += 1
                (euro_record if is_euro else league_record)['w'] += 1
            elif team_gf < team_ga:
                losses += 1
                (euro_record if is_euro else league_record)['l'] += 1
            else:
                draws += 1
                (euro_record if is_euro else league_record)['d'] += 1

            prefix_for     = 'team_a' if is_home else 'team_b'
            prefix_against = 'team_b' if is_home else 'team_a'

            def _safe(val): return max(val, 0)

            corners_for.append(_safe(match.get(f'{prefix_for}_corners', 0)))
            corners_against.append(_safe(match.get(f'{prefix_against}_corners', 0)))
            shots_for.append(_safe(match.get(f'{prefix_for}_shots', 0)))
            shots_against.append(_safe(match.get(f'{prefix_against}_shots', 0)))
            sot_for.append(_safe(match.get(f'{prefix_for}_shotsOnTarget', 0)))
            sot_against.append(_safe(match.get(f'{prefix_against}_shotsOnTarget', 0)))
            cards_for.append(_safe(match.get(f'{prefix_for}_cards_num', 0)))
            cards_against.append(_safe(match.get(f'{prefix_against}_cards_num', 0)))
            offsides_for.append(_safe(match.get(f'{prefix_for}_offsides', 0)))
            offsides_against.append(_safe(match.get(f'{prefix_against}_offsides', 0)))
            fouls_for.append(_safe(match.get(f'{prefix_for}_fouls', 0)))
            fouls_against.append(_safe(match.get(f'{prefix_against}_fouls', 0)))

            goal_key = f'{prefix_for}_goal_details'
            card_key = f'{prefix_for}_card_details'

            for goal in match.get(goal_key, []):
                pid = goal.get('player_id')
                if pid:
                    pname = self._get_player_name(pid)
                    player_goals[pname] = player_goals.get(pname, 0) + 1
                aid = goal.get('assist_player_id', -1)
                if aid and aid != -1:
                    aname = self._get_player_name(aid)
                    player_assists[aname] = player_assists.get(aname, 0) + 1

            for card in match.get(card_key, []):
                if card.get('card_type') in ['Yellow', 'Second Yellow', 'Red']:
                    pid = card.get('player_id')
                    if pid:
                        pname = self._get_player_name(pid)
                        player_cards[pname] = player_cards.get(pname, 0) + 1

        n = len(match_details)
        points = wins * 3 + draws

        print(f"Record:       {wins}W - {draws}D - {losses}L ({points} points from {n * 3})")

        # Show per-competition breakdown if there are European games in the set
        has_euro = euro_record['w'] + euro_record['d'] + euro_record['l'] > 0
        has_league = league_record['w'] + league_record['d'] + league_record['l'] > 0
        if has_euro and has_league:
            lr = league_record
            er = euro_record
            print(f"  League:     {lr['w']}W-{lr['d']}D-{lr['l']}L  |  "
                  f"European:   {er['w']}W-{er['d']}D-{er['l']}L")

        print(f"Goals:        {gf} scored ({safe_divide(gf, n):.1f}/gm) | {ga} conceded ({safe_divide(ga, n):.1f}/gm)")
        print()

        def avg(lst): return safe_divide(sum(lst), len(lst)) if lst else 0

        print(f"TEAM AVERAGES (Last {n})")
        print(f"  Corners:    {avg(corners_for):.1f} per game (opponents: {avg(corners_against):.1f})")
        print(f"  Shots:      {avg(shots_for):.1f} per game (opponents: {avg(shots_against):.1f})")
        print(f"  SOT:        {avg(sot_for):.1f} per game (opponents: {avg(sot_against):.1f})")
        print(f"  Cards:      {avg(cards_for):.1f} per game (opponents: {avg(cards_against):.1f})")
        print(f"  Offsides:   {avg(offsides_for):.1f} per game (opponents: {avg(offsides_against):.1f})")
        print(f"  Fouls:      {avg(fouls_for):.1f} per game (opponents: {avg(fouls_against):.1f})")
        print()

        print(f"PLAYER STATS (Last {n})")
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

        # Form trend — only meaningful if all matches are from the same competition type
        # With mixed comps, we show it but note the caveat
        if n >= 10:
            first_5_ppg = safe_divide(
                sum(3 if self._get_result(match_details[i]) == 'W' else
                    1 if self._get_result(match_details[i]) == 'D' else 0
                    for i in range(5)), 5
            )
            last_5_ppg = safe_divide(
                sum(3 if self._get_result(match_details[i]) == 'W' else
                    1 if self._get_result(match_details[i]) == 'D' else 0
                    for i in range(5, 10)), 5
            )

            if last_5_ppg > first_5_ppg:
                trend = "↗️ IMPROVING"
            elif last_5_ppg < first_5_ppg:
                trend = "↘️ DECLINING"
            else:
                trend = "→ STABLE"

            note = " (all competitions)" if has_euro and has_league else ""
            print(f"Form Trend: {trend} (most recent 5 vs previous 5{note})")
        print()

    def _get_result(self, match: Dict) -> str:
        is_home    = match.get('homeID') == self.team_id
        home_goals = match.get('homeGoalCount', 0)
        away_goals = match.get('awayGoalCount', 0)
        if is_home:
            return 'W' if home_goals > away_goals else 'L' if home_goals < away_goals else 'D'
        else:
            return 'W' if away_goals > home_goals else 'L' if away_goals < home_goals else 'D'