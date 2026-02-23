"""
fixtures.py
Browse fixtures by date. Priority leagues shown first.
Each fixture shows two lines: team names + score/vs, then comp form and overall form.
"""

import sys
import calendar
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent))
from betting.data_loader import DataLoader


# ---------------------------------------------------------------------------
# League ordering
# ---------------------------------------------------------------------------

PRIORITY_LEAGUE_KEYS = [
    "champions_league",
    "europa_league",
    "europa_conference_league",
    "england_premier_league",
    "england_championship",
    "england_league_one",
    "england_league_two",
    "spain_la_liga",
    "germany_bundesliga",
    "italy_serie_a",
    "france_ligue_1",
]

PRIORITY_SET = set(PRIORITY_LEAGUE_KEYS)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _unix_to_local(ts: int) -> datetime:
    return datetime.fromtimestamp(ts)


def _build_position_map(league_table: Optional[Dict]) -> Dict[int, int]:
    """Extract {team_id: position} from whatever shape league_table.json takes."""
    if not league_table:
        return {}

    standings = None

    if isinstance(league_table, list):
        standings = league_table
    elif isinstance(league_table, dict):
        for key in ("standings", "table", "data", "results"):
            if isinstance(league_table.get(key), list):
                standings = league_table[key]
                break
        if standings is None:
            overall = league_table.get("overall")
            if isinstance(overall, list):
                standings = overall
            elif isinstance(overall, dict):
                for key in ("standings", "table", "data"):
                    if isinstance(overall.get(key), list):
                        standings = overall[key]
                        break
        if standings is None:
            for v in league_table.values():
                if isinstance(v, list) and v:
                    standings = v
                    break

    if not standings:
        return {}

    positions = {}
    for i, entry in enumerate(standings, start=1):
        if not isinstance(entry, dict):
            continue
        team_id = entry.get("id") or entry.get("team_id") or entry.get("teamId")
        pos = entry.get("position") or entry.get("pos") or entry.get("rank") or i
        if team_id is not None:
            try:
                positions[int(team_id)] = int(pos)
            except (ValueError, TypeError):
                pass

    return positions


def _get_result(match: Dict, team_id: int) -> str:
    """Return W / D / L for team_id in this completed match."""
    is_home = match.get("homeID") == team_id
    hg = match.get("homeGoalCount", 0)
    ag = match.get("awayGoalCount", 0)
    if is_home:
        if hg > ag: return "W"
        if hg < ag: return "L"
        return "D"
    else:
        if ag > hg: return "W"
        if ag < hg: return "L"
        return "D"


# ---------------------------------------------------------------------------
# Form map builders
# ---------------------------------------------------------------------------

def _build_overall_form_map(all_league_matches: List[Tuple]) -> Dict[int, str]:
    """
    {team_id: 'WWDLW'} — last 5 results across ALL competitions combined.
    """
    all_complete = []
    for _key, _sid, matches in all_league_matches:
        for m in matches:
            if m.get("status") == "complete":
                all_complete.append(m)

    all_complete.sort(key=lambda m: m.get("date_unix") or 0)

    team_results: Dict[int, List[str]] = {}
    for m in all_complete:
        for id_key in ("homeID", "awayID"):
            tid = m.get(id_key)
            if tid is None:
                continue
            tid = int(tid)
            team_results.setdefault(tid, []).append(_get_result(m, tid))

    return {tid: "".join(results[-5:]) for tid, results in team_results.items()}


def _build_comp_form_maps(all_league_matches: List[Tuple]) -> Dict[str, Dict[int, str]]:
    """
    {league_key: {team_id: 'WWDLW'}} — last 5 results within each specific competition.
    """
    # Collect completed matches per league key, sorted by date
    per_league: Dict[str, List[Dict]] = {}
    for league_key, _sid, matches in all_league_matches:
        complete = sorted(
            [m for m in matches if m.get("status") == "complete"],
            key=lambda m: m.get("date_unix") or 0
        )
        per_league[league_key] = complete

    comp_form_maps: Dict[str, Dict[int, str]] = {}
    for league_key, matches in per_league.items():
        team_results: Dict[int, List[str]] = {}
        for m in matches:
            for id_key in ("homeID", "awayID"):
                tid = m.get(id_key)
                if tid is None:
                    continue
                tid = int(tid)
                team_results.setdefault(tid, []).append(_get_result(m, tid))
        comp_form_maps[league_key] = {
            tid: "".join(results[-5:]) for tid, results in team_results.items()
        }

    return comp_form_maps


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_all_league_data(loader: DataLoader):
    """
    Load matches + tables for every available league.
    Returns:
        league_info_map : {league_key: league_dict}
        league_matches  : [(league_key, season_id, [matches])]
        position_maps   : {league_key: {team_id: position}}
    """
    leagues = loader.get_available_leagues()
    league_info_map: Dict = {}
    league_matches: List[Tuple] = []
    position_maps: Dict = {}

    for league in leagues:
        key = league["key"]
        sid = league["season_id"]
        league_info_map[key] = league

        matches = loader.load_all_matches(key, sid)
        league_matches.append((key, sid, matches))

        table = loader.load_league_table(key, sid)
        position_maps[key] = _build_position_map(table)

    return league_info_map, league_matches, position_maps


def get_fixtures_for_date(
    target_date: date,
    league_matches: List[Tuple],
) -> Dict[str, List[Dict]]:
    """Return {league_key: [matches on target_date sorted by ko]}."""
    result: Dict[str, List[Dict]] = {}
    for league_key, _sid, matches in league_matches:
        day_matches = [
            m for m in matches
            if (ts := m.get("date_unix") or m.get("timestamp"))
            and _unix_to_local(ts).date() == target_date
        ]
        if day_matches:
            day_matches.sort(key=lambda m: m.get("date_unix") or 0)
            result[league_key] = day_matches
    return result


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

# Width of team column (name + position), used to align the form line below
TEAM_COL_WIDTH = 42


def _team_header(name: str, pos: Optional[int]) -> str:
    pos_str = f" ({_ordinal(pos)})" if pos else ""
    return f"{name}{pos_str}"


def _form_str(comp_form: str, overall_form: str) -> str:
    parts = []
    if comp_form:
        parts.append(f"Comp: {comp_form}")
    if overall_form:
        parts.append(f"Overall: {overall_form}")
    return "  ".join(parts)


def _print_fixture(
    match: Dict,
    pos_map: Dict[int, int],
    comp_form_map: Dict[int, str],
    overall_form_map: Dict[int, str],
) -> None:
    home_id   = match.get("homeID")
    away_id   = match.get("awayID")
    home_name = match.get("home_name") or match.get("home") or "Unknown"
    away_name = match.get("away_name") or match.get("away") or "Unknown"

    ts = match.get("date_unix") or match.get("timestamp") or 0
    ko = _unix_to_local(ts).strftime("%H:%M") if ts else "--:--"

    home_pos = pos_map.get(int(home_id)) if home_id is not None else None
    away_pos = pos_map.get(int(away_id)) if away_id is not None else None

    home_header = _team_header(home_name, home_pos)
    away_header = _team_header(away_name, away_pos)

    status = match.get("status", "fixture")
    if status == "complete":
        hg = match.get("homeGoalCount", "?")
        ag = match.get("awayGoalCount", "?")
        mid = f"{hg} - {ag}"
    else:
        mid = "vs"

    # Line 1: ko  Home Team (Nth)      score/vs      Away Team (Nth)
    line1 = f"  {ko}  {home_header:<{TEAM_COL_WIDTH}}  {mid:^7}  {away_header}"
    print(line1)

    # Line 2: form strings, aligned under each team column
    home_comp    = comp_form_map.get(int(home_id), "") if home_id is not None else ""
    home_overall = overall_form_map.get(int(home_id), "") if home_id is not None else ""
    away_comp    = comp_form_map.get(int(away_id), "") if away_id is not None else ""
    away_overall = overall_form_map.get(int(away_id), "") if away_id is not None else ""

    home_form = _form_str(home_comp, home_overall)
    away_form = _form_str(away_comp, away_overall)

    if home_form or away_form:
        # Indent to match team column start (len("  HH:MM  ") = 9)
        indent = " " * 9
        line2 = f"{indent}{home_form:<{TEAM_COL_WIDTH + 10}}  {away_form}"
        print(line2)


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def display_fixtures(
    target_date: date,
    league_info_map: Dict,
    league_matches: List[Tuple],
    position_maps: Dict,
) -> None:

    fixtures_by_league = get_fixtures_for_date(target_date, league_matches)
    overall_form_map   = _build_overall_form_map(league_matches)
    comp_form_maps     = _build_comp_form_maps(league_matches)

    day_label = target_date.strftime("%a %d %B %Y").lstrip("0")
    print(f"\n{day_label}")
    print("═" * 70)

    # --- Priority leagues ---
    no_fixture_leagues = []

    for league_key in PRIORITY_LEAGUE_KEYS:
        league = league_info_map.get(league_key)
        if not league:
            continue

        matches = fixtures_by_league.get(league_key, [])

        if not matches:
            no_fixture_leagues.append(league["name"])
            continue

        league_name = league["name"].upper()
        pos_map     = position_maps.get(league_key, {})
        comp_form   = comp_form_maps.get(league_key, {})

        print(f"\n{league_name}")
        for m in matches:
            _print_fixture(m, pos_map, comp_form, overall_form_map)

    # Collapsed no-fixture line at the bottom of the priority block
    if no_fixture_leagues:
        print(f"\nNo fixtures today:")
        print(f"  {' · '.join(no_fixture_leagues)}")

    # --- Rest of world (only shown if they have fixtures) ---
    rest_keys = sorted(
        [k for k in fixtures_by_league if k not in PRIORITY_SET],
        key=lambda k: league_info_map.get(k, {}).get("name", k)
    )

    if rest_keys:
        print(f"\n{'─' * 70}")
        for league_key in rest_keys:
            league      = league_info_map.get(league_key)
            league_name = league["name"].upper() if league else league_key.upper()
            pos_map     = position_maps.get(league_key, {})
            comp_form   = comp_form_maps.get(league_key, {})
            matches     = fixtures_by_league[league_key]

            print(f"\n{league_name}")
            for m in matches:
                _print_fixture(m, pos_map, comp_form, overall_form_map)

    print(f"\n{'═' * 70}\n")


# ---------------------------------------------------------------------------
# Date selection
# ---------------------------------------------------------------------------

def select_date() -> date:
    today = date.today()

    print(f"\n  1. Today ({today.strftime('%a %d %b %Y')})")
    print("  2. Choose a date")

    while True:
        raw = input("\nEnter number: ").strip()
        if raw == "1":
            return today
        if raw == "2":
            break
        print("  Invalid choice, try again.")

    # Year
    current_year = today.year
    year_options = list(range(current_year - 1, current_year + 2))
    print("\nSelect year:")
    for i, y in enumerate(year_options, 1):
        print(f"  {i:>3}. {y}")
    while True:
        raw = input("\nEnter number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(year_options):
            year = year_options[int(raw) - 1]
            break
        print("  Invalid choice, try again.")

    # Month
    print("\nSelect month:")
    for m in range(1, 13):
        label = calendar.month_name[m]
        if year == today.year and m == today.month:
            label += " (current)"
        print(f"  {m:>3}. {label}")
    while True:
        raw = input("\nEnter number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= 12:
            month = int(raw)
            break
        print("  Invalid choice, try again.")

    # Day
    _, days_in_month = calendar.monthrange(year, month)
    print("\nSelect day:")
    for d in range(1, days_in_month + 1):
        label = str(d)
        if year == today.year and month == today.month and d == today.day:
            label += " (today)"
        print(f"  {d:>3}. {label}")
    while True:
        raw = input("\nEnter number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= days_in_month:
            return date(year, month, int(raw))
        print("  Invalid choice, try again.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    loader = DataLoader(data_dir="./data")

    print("\nFIXTURE BROWSER")

    print("\nLoading data...", end="", flush=True)
    league_info_map, league_matches, position_maps = load_all_league_data(loader)
    print(" done.")

    while True:
        target_date = select_date()
        display_fixtures(target_date, league_info_map, league_matches, position_maps)

        again = input("Browse another date? (y/n): ").strip().lower()
        if again != "y":
            break


if __name__ == "__main__":
    main()