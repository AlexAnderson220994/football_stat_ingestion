"""
H2H Analysis - Head to head breakdown
"""

from typing import Dict, List, Optional
from betting.utils import format_date


EUROPEAN_KEYS = {'champions_league', 'europa_league', 'europa_conference_league'}


class H2HAnalysis:
    """Detailed H2H analysis"""

    def __init__(self, team_id: int, team_name: str, all_players: List[Dict]):
        self.team_id = team_id
        self.team_name = team_name
        self.all_players = all_players

    def print_h2h_analysis(self, h2h_match: Dict, opponent_name: str, competition_label: str = ""):
        """
        Print detailed H2H analysis.

        Args:
            h2h_match: Match detail dict for the most recent meeting.
            opponent_name: Name of the opponent.
            competition_label: Optional label e.g. '[UCL]' to show which comp the H2H was in.
        """
        comp_str = f" {competition_label}" if competition_label else ""
        print("=" * 80)
        print(f"🔥 HEAD-TO-HEAD vs {opponent_name.upper()} (Next Opponent){comp_str}")
        print("=" * 80)
        print()

        if not h2h_match:
            print("No previous H2H data available")
            print()
            return

        home_name  = h2h_match.get('home_name', 'Unknown')
        away_name  = h2h_match.get('away_name', 'Unknown')
        home_goals = h2h_match.get('homeGoalCount', 0)
        away_goals = h2h_match.get('awayGoalCount', 0)
        date       = format_date(h2h_match.get('date_unix', 0))
        is_home    = h2h_match.get('homeID') == self.team_id

        print(f"Last Meeting: {home_name} {home_goals}-{away_goals} {away_name} ({date})")
        print("-" * 80)

        h_corners  = max(h2h_match.get('team_a_corners', 0), 0)
        a_corners  = max(h2h_match.get('team_b_corners', 0), 0)
        h_shots    = max(h2h_match.get('team_a_shots', 0), 0)
        a_shots    = max(h2h_match.get('team_b_shots', 0), 0)
        h_sot      = max(h2h_match.get('team_a_shotsOnTarget', 0), 0)
        a_sot      = max(h2h_match.get('team_b_shotsOnTarget', 0), 0)
        h_cards    = max(h2h_match.get('team_a_cards_num', 0), 0)
        a_cards    = max(h2h_match.get('team_b_cards_num', 0), 0)
        h_offsides = max(h2h_match.get('team_a_offsides', 0), 0)
        a_offsides = max(h2h_match.get('team_b_offsides', 0), 0)
        h_fouls    = max(h2h_match.get('team_a_fouls', 0), 0)
        a_fouls    = max(h2h_match.get('team_b_fouls', 0), 0)
        h_poss     = max(h2h_match.get('team_a_possession', 0), 0)
        a_poss     = max(h2h_match.get('team_b_possession', 0), 0)

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

        goals_list = h2h_match.get('team_a_goal_details', []) if is_home else h2h_match.get('team_b_goal_details', [])
        if goals_list:
            goal_scorers = []
            for goal in goals_list:
                player_id = goal.get('player_id')
                player_name = self._get_player_name(player_id) if player_id else "Unknown"
                time = goal.get('time', '?')
                goal_type = goal.get('type', '')
                type_str = f" {goal_type}" if goal_type and goal_type != 'Goal' else ""
                goal_scorers.append(f"{player_name} ({time}'{type_str})")
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

        cards_list = h2h_match.get('team_a_card_details', []) if is_home else h2h_match.get('team_b_card_details', [])
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

        print()
        self._print_h2h_summary(h2h_match, is_home, home_goals, away_goals, home_name, away_name)

    def _get_player_name(self, player_id: int) -> str:
        if not self.all_players:
            return "Unknown"
        for player in self.all_players:
            if player.get('id') == player_id:
                return player.get('known_as', player.get('full_name', 'Unknown'))
        return "Unknown"

    def _print_h2h_summary(self, match: Dict, is_home: bool, home_goals: int, away_goals: int,
                           home_name: str, away_name: str):
        print("H2H SUMMARY")

        if is_home:
            result = "Win" if home_goals > away_goals else "Loss" if home_goals < away_goals else "Draw"
        else:
            result = "Win" if away_goals > home_goals else "Loss" if away_goals < home_goals else "Draw"

        print(f"  Result:        {home_goals}-{away_goals} {result}")

        h_poss    = max(match.get('team_a_possession', 0), 0)
        a_poss    = max(match.get('team_b_possession', 0), 0)
        team_poss = h_poss if is_home else a_poss

        if team_poss < 45:
            poss_analysis = f"Struggled for possession ({team_poss}%)"
        elif team_poss > 55:
            poss_analysis = f"Dominated possession ({team_poss}%)"
        else:
            poss_analysis = f"Even possession ({team_poss}%)"
        print(f"  Possession:    {poss_analysis}")

        h_shots    = max(match.get('team_a_shots', 0), 0)
        a_shots    = max(match.get('team_b_shots', 0), 0)
        team_shots = h_shots if is_home else a_shots
        opp_shots  = a_shots if is_home else h_shots

        shots_analysis = (f"More shots ({team_shots} vs {opp_shots})"
                          if team_shots > opp_shots
                          else f"Fewer shots ({team_shots} vs {opp_shots})")

        h_cards    = max(match.get('team_a_cards_num', 0), 0)
        a_cards    = max(match.get('team_b_cards_num', 0), 0)
        team_cards = h_cards if is_home else a_cards
        opp_cards  = a_cards if is_home else h_cards

        if team_cards < opp_cards:
            discipline = f"Controlled ({team_cards} card vs {opp_cards})"
        elif team_cards > opp_cards:
            discipline = f"Undisciplined ({team_cards} cards vs {opp_cards})"
        else:
            discipline = f"Even discipline ({team_cards} cards each)"
        print(f"  Discipline:    {discipline}")

        h_sot    = max(match.get('team_a_shotsOnTarget', 0), 0)
        a_sot    = max(match.get('team_b_shotsOnTarget', 0), 0)
        team_sot = h_sot if is_home else a_sot

        if team_shots > 0:
            accuracy = (team_sot / team_shots) * 100
            print(f"  Threat:        {shots_analysis} | Shot accuracy {accuracy:.0f}% ({team_sot}/{team_shots})")

        print()