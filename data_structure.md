# Football Betting System - Complete Data Structure Documentation

---

## Table of Contents
1. [Directory Structure](#directory-structure)
2. [League Metadata](#1-league-metadata)
3. [League Table](#2-league-table)
4. [Match Summary](#3-match-summary)
5. [Match Details (Full)](#4-match-details-full)
6. [Team Data](#5-team-data)
7. [Player Data](#6-player-data)
8. [H2H Data](#7-h2h-data)
9. [Field Name Reference](#field-name-reference)
10. [Critical Implementation Notes](#critical-implementation-notes)

---

## Directory Structure

```
project_root/
├── data/
│   ├── leagues/
│   │   └── {league_key}_{season_id}/
│   │       ├── metadata.json
│   │       ├── league_table.json
│   │       ├── matches/
│   │       │   └── {match_id}.json
│   │       ├── match_details/
│   │       │   └── {match_id}.json
│   │       ├── players/
│   │       │   └── {player_id}.json
│   │       └── h2h/
│   │           └── {team_a_id}_vs_{team_b_id}.json
│   └── teams/
│       └── {team_name}_{team_id}/
│           ├── team_info.json
│           ├── all_fixtures.json
│           └── all_stats.json
```

---

## 1. League Metadata

### File Path
```
data/leagues/{league_key}_{season_id}/metadata.json
```

### Example Path
```
data/leagues/england_premier_league_15050/metadata.json
```

### Structure
```json
{
  "league_name": "England Premier League",
  "league_key": "england_premier_league",
  "season_id": 15050,
  "competition_id": 15050,
  "last_updated": "2026-02-03T15:52:16.784253"
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `league_name` | string | Human-readable league name |
| `league_key` | string | Underscore-separated identifier (e.g., "england_premier_league") |
| `season_id` | integer | Season identifier |
| `competition_id` | integer | Competition identifier |
| `last_updated` | string | ISO 8601 timestamp of last update |

---

## 2. League Table

### File Path
```
data/leagues/{league_key}_{season_id}/league_table.json
```

### Example Path
```
data/leagues/england_premier_league_15050/league_table.json
```

### Structure (League Format)
```json
{
  "data": {
    "league_table": [
      {
        "id": 149,
        "name": "Manchester United",
        "position": 5,
        "points": 45,
        "matchesPlayed": 23,
        "matchesWon": 13,
        "matchesDrawn": 6,
        "matchesLost": 4,
        "seasonGoals": 38,
        "seasonGoals_home": 22,
        "seasonGoals_away": 16,
        "seasonConceded": 20,
        "seasonConceded_home": 8,
        "seasonConceded_away": 12,
        "seasonGoalDifference": 18,
        "seasonWins_overall": 13,
        "seasonWins_home": 8,
        "seasonWins_away": 5,
        "seasonDraws_overall": 6,
        "seasonDraws_home": 3,
        "seasonDraws_away": 3,
        "seasonLosses_overall": 4,
        "seasonLosses_home": 1,
        "seasonLosses_away": 3,
        "ppg_overall": 1.96,
        "ppg_home": 2.25,
        "ppg_away": 1.67
      }
    ],
    "specific_tables": []
  }
}
```

### Fields in `league_table` Array

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Team ID |
| `name` | string | Team name |
| `position` | integer | Current league position |
| `points` | integer | Total points |
| `matchesPlayed` | integer | Matches played |
| `matchesWon` | integer | Matches won |
| `matchesDrawn` | integer | Matches drawn |
| `matchesLost` | integer | Matches lost |
| `seasonGoals` | integer | Total goals scored |
| `seasonGoals_home` | integer | Goals scored at home |
| `seasonGoals_away` | integer | Goals scored away |
| `seasonConceded` | integer | Total goals conceded |
| `seasonConceded_home` | integer | Goals conceded at home |
| `seasonConceded_away` | integer | Goals conceded away |
| `seasonGoalDifference` | integer | Goal difference |
| `seasonWins_overall` | integer | Total wins |
| `seasonWins_home` | integer | Home wins |
| `seasonWins_away` | integer | Away wins |
| `seasonDraws_overall` | integer | Total draws |
| `seasonDraws_home` | integer | Home draws |
| `seasonDraws_away` | integer | Away draws |
| `seasonLosses_overall` | integer | Total losses |
| `seasonLosses_home` | integer | Home losses |
| `seasonLosses_away` | integer | Away losses |
| `ppg_overall` | float | Points per game overall |
| `ppg_home` | float | Points per game at home |
| `ppg_away` | float | Points per game away |

### Alternative Structure (Tournament/Cup Format)

```json
{
  "data": {
    "specific_tables": [
      {
        "round_name": "Group Stage",
        "groups": [
          {
            "group_name": "Group A",
            "table": [
              {
                "id": 149,
                "name": "Manchester United",
                "position": 1,
                "points": 9,
                "matchesPlayed": 3
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 3. Match Summary

### File Path
```
data/leagues/{league_key}_{season_id}/matches/{match_id}.json
```

### Example Path
```
data/leagues/england_premier_league_15050/matches/8223489.json
```

### Structure
```json
{
  "id": 8223489,
  "homeID": 149,
  "awayID": 152,
  "season": "2025/2026",
  "status": "complete",
  "roundID": 120208,
  "game_week": 5,
  "revised_game_week": -1,
  "homeGoalCount": 2,
  "awayGoalCount": 1,
  "totalGoalCount": 3,
  "date_unix": 1758385800,
  "winningTeam": 149,
  "no_home_away": 0,
  "home_name": "Manchester United",
  "away_name": "Chelsea",
  "home_url": "/clubs/manchester-united-fc-149",
  "away_url": "/clubs/chelsea-fc-152",
  "home_image": "teams/england-manchester-united-fc.png",
  "away_image": "teams/england-chelsea-fc.png",
  "competition_id": 15050
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Match ID |
| `homeID` | integer | Home team ID |
| `awayID` | integer | Away team ID |
| `season` | string | Season (e.g., "2025/2026") |
| `status` | string | "complete", "incomplete", "postponed" |
| `roundID` | integer | Round ID |
| `game_week` | integer | Gameweek number |
| `revised_game_week` | integer | Revised gameweek (-1 if not revised) |
| `homeGoalCount` | integer | Home team goals |
| `awayGoalCount` | integer | Away team goals |
| `totalGoalCount` | integer | Total goals |
| `date_unix` | integer | Unix timestamp |
| `winningTeam` | integer | Winning team ID (0 = draw) |
| `no_home_away` | integer | 0 = normal match, 1 = neutral venue |
| `home_name` | string | Home team name |
| `away_name` | string | Away team name |
| `home_url` | string | Home team URL |
| `away_url` | string | Away team URL |
| `home_image` | string | Home team image path |
| `away_image` | string | Away team image path |
| `competition_id` | integer | Competition ID |

---

## 4. Match Details (Full)

### File Path
```
data/leagues/{league_key}_{season_id}/match_details/{match_id}.json
```

### Example Path
```
data/leagues/england_premier_league_15050/match_details/8223489.json
```

### ⚠️ CRITICAL: Field Naming Convention

**In match_details files, statistics use `team_a` and `team_b` notation:**
- `team_a_*` = Home team
- `team_b_*` = Away team

**DO NOT use `home_*` or `away_*` for stats!**

### Core Match Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Match ID |
| `homeID` | integer | Home team ID |
| `awayID` | integer | Away team ID |
| `home_name` | string | Home team name |
| `away_name` | string | Away team name |
| `season` | string | Season |
| `status` | string | Match status |
| `game_week` | integer | Gameweek number |
| `date_unix` | integer | Unix timestamp |
| `winningTeam` | integer | Winner ID (0 = draw) |
| `competition_id` | integer | Competition ID |

### Goals

| Field | Type | Description |
|-------|------|-------------|
| `homeGoals` | array[string] | Goal times ["14", "37"] |
| `awayGoals` | array[string] | Goal times ["80"] |
| `homeGoalCount` | integer | Home team goals |
| `awayGoalCount` | integer | Away team goals |
| `totalGoalCount` | integer | Total goals |
| `ht_goals_team_a` | integer | Home team 1st half goals |
| `ht_goals_team_b` | integer | Away team 1st half goals |
| `goals_2hg_team_a` | integer | Home team 2nd half goals |
| `goals_2hg_team_b` | integer | Away team 2nd half goals |
| `HTGoalCount` | integer | Total 1st half goals |
| `GoalCount_2hg` | integer | Total 2nd half goals |
| `btts` | boolean | Both teams scored |

### Corners

| Field | Type | Description |
|-------|------|-------------|
| `team_a_corners` | integer | Home team total corners |
| `team_b_corners` | integer | Away team total corners |
| `totalCornerCount` | integer | Match total corners |
| `team_a_fh_corners` | integer | Home team 1st half corners |
| `team_b_fh_corners` | integer | Away team 1st half corners |
| `team_a_2h_corners` | integer | Home team 2nd half corners |
| `team_b_2h_corners` | integer | Away team 2nd half corners |
| `corner_fh_count` | integer | Total 1st half corners |
| `corner_2h_count` | integer | Total 2nd half corners |

### Shots

| Field | Type | Description |
|-------|------|-------------|
| `team_a_shots` | integer | Home team total shots |
| `team_b_shots` | integer | Away team total shots |
| `team_a_shotsOnTarget` | integer | Home shots on target |
| `team_b_shotsOnTarget` | integer | Away shots on target |
| `team_a_shotsOffTarget` | integer | Home shots off target |
| `team_b_shotsOffTarget` | integer | Away shots off target |

### Cards

| Field | Type | Description |
|-------|------|-------------|
| `team_a_cards_num` | integer | Home team total cards |
| `team_b_cards_num` | integer | Away team total cards |
| `team_a_yellow_cards` | integer | Home yellow cards |
| `team_b_yellow_cards` | integer | Away yellow cards |
| `team_a_red_cards` | integer | Home red cards |
| `team_b_red_cards` | integer | Away red cards |
| `team_a_fh_cards` | integer | Home 1st half cards |
| `team_b_fh_cards` | integer | Away 1st half cards |
| `team_a_2h_cards` | integer | Home 2nd half cards |
| `team_b_2h_cards` | integer | Away 2nd half cards |
| `total_fh_cards` | integer | Total 1st half cards |
| `total_2h_cards` | integer | Total 2nd half cards |

### Other Match Stats

| Field | Type | Description |
|-------|------|-------------|
| `team_a_possession` | integer | Home possession % |
| `team_b_possession` | integer | Away possession % |
| `team_a_fouls` | integer | Home fouls |
| `team_b_fouls` | integer | Away fouls |
| `team_a_offsides` | integer | Home offsides |
| `team_b_offsides` | integer | Away offsides |
| `team_a_attacks` | integer | Home attacks |
| `team_b_attacks` | integer | Away attacks |
| `team_a_dangerous_attacks` | integer | Home dangerous attacks |
| `team_b_dangerous_attacks` | integer | Away dangerous attacks |
| `team_a_xg` | float | Home expected goals |
| `team_b_xg` | float | Away expected goals |
| `total_xg` | float | Total expected goals |
| `team_a_throwins` | integer | Home throw-ins |
| `team_b_throwins` | integer | Away throw-ins |
| `team_a_freekicks` | integer | Home free kicks |
| `team_b_freekicks` | integer | Away free kicks |
| `team_a_goalkicks` | integer | Home goal kicks |
| `team_b_goalkicks` | integer | Away goal kicks |

### Penalties

| Field | Type | Description |
|-------|------|-------------|
| `team_a_penalties_won` | integer | Home penalties won |
| `team_b_penalties_won` | integer | Away penalties won |
| `team_a_penalty_goals` | integer | Home penalty goals scored |
| `team_b_penalty_goals` | integer | Away penalty goals scored |
| `team_a_penalty_missed` | integer | Home penalties missed |
| `team_b_penalty_missed` | integer | Away penalties missed |

### Data Quality Indicators

| Field | Type | Description |
|-------|------|-------------|
| `corner_timings_recorded` | integer | 1 = partial, 2 = full data |
| `card_timings_recorded` | integer | 1 = partial, 2 = full data |
| `attacks_recorded` | integer | 1 = data available |
| `goal_timings_recorded` | integer | 1 = data available |
| `pens_recorded` | integer | 1 = data available |
| `throwins_recorded` | integer | 1 = data available |
| `freekicks_recorded` | integer | 1 = data available |
| `goalkicks_recorded` | integer | 1 = data available |

### Lineups Structure

```json
{
  "lineups": {
    "team_a": [
      {
        "player_id": 40011,
        "shirt_number": 1,
        "player_events": []
      },
      {
        "player_id": 18226,
        "shirt_number": 8,
        "player_events": [
          {
            "event_type": "Goal",
            "event_time": "14"
          }
        ]
      }
    ],
    "team_b": [...]
  }
}
```

**Lineup Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | integer | Player ID |
| `shirt_number` | integer | Jersey number |
| `player_events` | array | Events this player was involved in |

**Player Events:**

| Field | Type | Description |
|-------|------|-------------|
| `event_type` | string | "Goal", "Yellow", "Red", "Second Yellow" |
| `event_time` | string | Time of event (e.g., "14", "45+5", "90+2") |

### Bench/Substitutes Structure

```json
{
  "bench": {
    "team_a": [
      {
        "player_in_id": 40090,
        "player_in_shirt_number": 7,
        "player_out_id": 147910,
        "player_out_time": "69'",
        "player_in_events": []
      }
    ],
    "team_b": [...]
  }
}
```

**Bench Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `player_in_id` | integer | Substitute player ID |
| `player_in_shirt_number` | integer | Substitute shirt number |
| `player_out_id` | integer | Replaced player ID (-1 if unused sub) |
| `player_out_time` | string | Substitution time ("69'", "-1" if unused) |
| `player_in_events` | array | Events after coming on |

### Goal Details Structure

```json
{
  "team_a_goal_details": [
    {
      "player_id": 18226,
      "time": "14",
      "extra": null,
      "assist_player_id": 840937,
      "type": "Right foot shot"
    }
  ],
  "team_b_goal_details": [...]
}
```

**Goal Detail Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | integer | Scorer player ID |
| `time` | string | Goal time ("14", "45+2", "90+6") |
| `extra` | string/null | Extra time indicator |
| `assist_player_id` | integer | Assisting player ID (0 if none) |
| `type` | string | "Right foot shot", "Header", "Left foot shot", "Penalty", etc. |

### Card Details Structure

```json
{
  "team_a_card_details": [
    {
      "player_id": 464625,
      "card_type": "Yellow",
      "time": "17"
    },
    {
      "player_id": 464625,
      "card_type": "Second Yellow",
      "time": "45+5"
    }
  ],
  "team_b_card_details": [...]
}
```

**Card Detail Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `player_id` | integer | Player ID receiving card |
| `card_type` | string | "Yellow", "Second Yellow", "Red" |
| `time` | string | Card time ("17", "90+6") |

### Betting Odds (Pre-match)

**Match Result:**
- `odds_ft_1` - Home win
- `odds_ft_x` - Draw
- `odds_ft_2` - Away win

**Goals Over/Under:**
- `odds_ft_over05` to `odds_ft_over45`
- `odds_ft_under05` to `odds_ft_under45`

**Both Teams to Score:**
- `odds_btts_yes`
- `odds_btts_no`

**Corners:**
- `odds_corners_over_75` to `odds_corners_over_115`
- `odds_corners_under_75` to `odds_corners_under_115`

### Odds Comparison Structure

```json
{
  "odds_comparison": {
    "FT Result": {
      "Home": {
        "bet365": "2.55",
        "Unibet": "2.50"
      },
      "Draw": {
        "bet365": "3.75"
      },
      "Away": {
        "bet365": "2.50"
      }
    },
    "Goals Over/Under": {
      "Over 2.5": {
        "bet365": "1.57"
      },
      "Under 2.5": {
        "bet365": "2.37"
      }
    },
    "Corners": {
      "Over 9.5": {
        "bet365": "1.70"
      },
      "Under 9.5": {
        "bet365": "2.11"
      }
    },
    "Both Teams To Score": {
      "Yes": {
        "bet365": "1.45"
      },
      "No": {
        "bet365": "2.50"
      }
    }
  }
}
```

### H2H Structure (in match_details)

```json
{
  "h2h": {
    "team_a_id": 149,
    "team_b_id": 152,
    "previous_matches_results": {
      "team_a_win_home": 10,
      "team_a_win_away": 6,
      "team_b_win_home": 13,
      "team_b_win_away": 3,
      "draw": 16,
      "team_a_wins": 16,
      "team_b_wins": 16,
      "totalMatches": 48,
      "team_a_win_percent": 33,
      "team_b_win_percent": 33
    },
    "betting_stats": {
      "over05": 44,
      "over15": 35,
      "over25": 23,
      "btts": 28,
      "avg_goals": 2.67,
      "total_goals": 128
    },
    "previous_matches_ids": [
      {
        "id": 7467043,
        "date_unix": 1747422900,
        "team_a_id": 152,
        "team_b_id": 149,
        "team_a_goals": 1,
        "team_b_goals": 0
      }
    ]
  }
}
```

---

## 5. Team Data

### Team Info
**Path:** `data/teams/{team_name}_{team_id}/team_info.json`

```json
{
  "team_id": 149,
  "team_name": "Manchester United",
  "competitions": [
    {
      "competition_id": 15050,
      "league_key": "england_premier_league",
      "season_id": 15050
    }
  ]
}
```

### Team Fixtures
**Path:** `data/teams/{team_name}_{team_id}/all_fixtures.json`

```json
{
  "team_id": 149,
  "team_name": "Manchester United",
  "fixtures": [
    {
      "id": 8223489,
      "homeID": 149,
      "awayID": 152,
      "status": "complete",
      "game_week": 5,
      "team_a_corners": 5,
      "team_b_corners": 5,
      "team_a_shots": 11,
      "team_b_shots": 5,
      "team_a_cards_num": 2,
      "team_b_cards_num": 7,
      "_league_key": "england_premier_league",
      "_season_id": 15050,
      "_competition_id": 15050
    }
  ]
}
```

**Important:** `_league_key`, `_season_id`, and `_competition_id` fields are added by the aggregator for filtering.

### Team Aggregated Stats
**Path:** `data/teams/{team_name}_{team_id}/all_stats.json`

```json
{
  "team_id": 149,
  "team_name": "Manchester United",
  "aggregated_stats": {
    "matches_played": 23,
    "wins": 13,
    "draws": 6,
    "losses": 4,
    "goals_scored": 38,
    "goals_conceded": 20,
    "clean_sheets": 11,
    "btts_count": 9,
    "btts_percentage": 39.13,
    "over_25_count": 14,
    "over_25_percentage": 60.87
  },
  "by_competition": {
    "england_premier_league_15050": {
      "competition_id": 15050,
      "league_key": "england_premier_league",
      "matches_played": 20,
      "wins": 11
    }
  }
}
```

---

## 6. Player Data

### File Path
```
data/leagues/{league_key}_{season_id}/players/{player_id}.json
```

### Example Path
```
data/leagues/england_premier_league_15050/players/464625.json
```

### Structure
```json
{
  "id": 464625,
  "full_name": "Bruno Fernandes",
  "known_as": "Bruno Fernandes",
  "position": "Midfielder",
  "age": 30,
  "height": 179,
  "weight": 69,
  "nationality": "Portugal",
  "club_team_id": 149,
  "minutes_played_overall": 1980,
  "minutes_played_home": 990,
  "minutes_played_away": 990,
  "appearances_overall": 22,
  "min_per_match": 90,
  "goals_overall": 8,
  "goals_home": 5,
  "goals_away": 3,
  "goals_per_90_overall": 0.36,
  "min_per_goal_overall": 247.5,
  "penalty_goals": 2,
  "assists_overall": 6,
  "assists_per_90_overall": 0.27,
  "cards_overall": 5,
  "yellow_cards_overall": 4,
  "red_cards_overall": 1,
  "cards_per_90_overall": 0.23,
  "min_per_card_overall": 396,
  "rank_in_league_top_attackers": 12,
  "rank_in_club_top_scorer": 2
}
```

### Player Fields

**Basic Info:**
- `id` - Player ID
- `full_name` - Full player name
- `known_as` - Common name/nickname
- `position` - "Goalkeeper", "Defender", "Midfielder", "Forward"
- `age` - Player age
- `height` - Height in cm
- `weight` - Weight in kg
- `nationality` - Nationality
- `club_team_id` - Current club ID

**Playing Time:**
- `minutes_played_overall` - Total minutes
- `minutes_played_home` - Home minutes
- `minutes_played_away` - Away minutes
- `appearances_overall` - Total appearances
- `min_per_match` - Average minutes per match

**Goals:**
- `goals_overall` - Total goals
- `goals_home` - Home goals
- `goals_away` - Away goals
- `goals_per_90_overall` - Goals per 90 minutes
- `min_per_goal_overall` - Minutes per goal
- `penalty_goals` - Penalty goals

**Assists:**
- `assists_overall` - Total assists
- `assists_per_90_overall` - Assists per 90 minutes
- `min_per_assist_overall` - Minutes per assist

**Discipline:**
- `cards_overall` - Total cards
- `yellow_cards_overall` - Yellow cards
- `red_cards_overall` - Red cards
- `cards_per_90_overall` - Cards per 90 minutes
- `min_per_card_overall` - Minutes per card

**Rankings:**
- `rank_in_league_top_attackers` - Rank in league (null if not applicable)
- `rank_in_league_top_midfielders` - Rank in league
- `rank_in_league_top_defenders` - Rank in league
- `rank_in_club_top_scorer` - Rank in club

---

## 7. H2H Data

### File Path
```
data/leagues/{league_key}_{season_id}/h2h/{team_a_id}_vs_{team_b_id}.json
```

### Structure
```json
{
  "team_a_id": 149,
  "team_b_id": 152,
  "previous_matches_results": {
    "team_a_win_home": 10,
    "team_a_win_away": 6,
    "team_b_win_home": 13,
    "team_b_win_away": 3,
    "draw": 16,
    "team_a_wins": 16,
    "team_b_wins": 16,
    "totalMatches": 48
  },
  "betting_stats": {
    "over05": 44,
    "over15": 35,
    "over25": 23,
    "btts": 28,
    "avg_goals": 2.67
  },
  "previous_matches_ids": [
    {
      "id": 7467043,
      "date_unix": 1747422900,
      "team_a_id": 152,
      "team_b_id": 149,
      "team_a_goals": 1,
      "team_b_goals": 0
    }
  ]
}
```

---

## Field Name Reference

### ⚠️ CRITICAL: Team Statistics Naming

**In `match_details` files, ALL stats use `team_a` and `team_b` notation:**

✅ **CORRECT:**
- `team_a_corners` - Home team corners
- `team_b_corners` - Away team corners
- `team_a_shots` - Home team shots
- `team_b_cards_num` - Home team cards
- `team_a_xg` - Home team expected goals

❌ **INCORRECT (DO NOT USE):**
- ~~`homeCorners`~~
- ~~`awayShots`~~
- ~~`home_cards`~~
- ~~`away_xg`~~

**Exception:** These basic fields still use home/away:
- `homeID`, `awayID` - Team IDs
- `homeGoalCount`, `awayGoalCount` - Goals
- `homeGoals`, `awayGoals` - Goal times
- `home_name`, `away_name` - Team names

### Common Field Patterns

**Corners:**
- `{team}_corners` - Total
- `{team}_fh_corners` - First half
- `{team}_2h_corners` - Second half

**Shots:**
- `{team}_shots` - Total
- `{team}_shotsOnTarget` - On target
- `{team}_shotsOffTarget` - Off target

**Cards:**
- `{team}_cards_num` - Total
- `{team}_yellow_cards` - Yellows
- `{team}_red_cards` - Reds
- `{team}_fh_cards` - First half
- `{team}_2h_cards` - Second half

**Goals:**
- `ht_goals_{team}` - First half
- `goals_2hg_{team}` - Second half

**Other:**
- `{team}_possession` - Possession %
- `{team}_fouls` - Fouls
- `{team}_offsides` - Offsides
- `{team}_xg` - Expected goals
- `{team}_attacks` - Attacks
- `{team}_dangerous_attacks` - Dangerous attacks

---

## Critical Implementation Notes

### 1. Backtesting - CRITICAL

**When backtesting gameweek N:**

```python
# Filter to ONLY data BEFORE target gameweek
target_gameweek = 5
calculator = StatCalculator(max_gameweek=target_gameweek)

# This filters fixtures to game_week < 5 (i.e., GW 1-4)
fixtures = calculator.filter_matches(all_fixtures)

# Calculate stats using ONLY GW 1-4 data
stats = calculator.calculate_team_averages(team_id, fixtures)

# Generate predictions (using GW 1-4 data)
predictions = predictor.predict(...)

# Compare to ACTUAL results from GW 5
actuals = extract_actuals(match_details_gw5)
```

**❌ NEVER include data from target_gameweek or later!**

### 2. Match Status Filtering

**Always filter to completed matches:**

```python
# Only use completed matches
fixtures = [f for f in fixtures if f['status'] == 'complete']
```

**Valid status values:**
- `"complete"` - Match finished (USE THIS)
- `"incomplete"` - Match not finished (EXCLUDE)
- `"postponed"` - Match postponed (EXCLUDE)

### 3. Player ID to Name Mapping

**To validate player predictions:**

```python
from betting.player_mapper import PlayerMapper

# Load players
home_players = loader.load_team_players(league_key, season_id, home_id)
away_players = loader.load_team_players(league_key, season_id, away_id)

# Create mapper
mapper = PlayerMapper(home_players, away_players)

# Check if player scored
for goal in match['team_a_goal_details']:
    scorer_id = goal['player_id']
    if mapper.matches_name(scorer_id, "Bruno Fernandes"):
        # Player scored!
        pass
```

### 4. Competition Filtering

**Filter team fixtures by competition:**

```python
# Load all fixtures
fixtures = loader.load_team_fixtures(team_id)['fixtures']

# Filter to specific league only
league_fixtures = [
    f for f in fixtures 
    if f.get('_league_key') == 'england_premier_league'
]
```

### 5. Data Quality Checks

**Before using specific stats, check recording indicators:**

```python
# Check if corner data is high quality
if match.get('corner_timings_recorded') == 2:
    # Use detailed corner timing data
    pass

# Check if attacks data is available
if match.get('attacks_recorded') == 1:
    # Use attacks data
    pass
```

**Values:**
- `0` - No data
- `1` - Partial data
- `2` - Full/high-quality data

### 6. Lineup Validation

**Lineups are ESSENTIAL for validating player props:**

```python
# Extract lineup
lineup_home = match['lineups']['team_a']
lineup_away = match['lineups']['team_b']

# Check player events
for player in lineup_home:
    for event in player['player_events']:
        if event['event_type'] == 'Goal':
            print(f"Player {player['player_id']} scored at {event['event_time']}")
```

### 7. bet365 Market Format

**Our predictions MUST match bet365 market names exactly:**

✅ **CORRECT:**
- "Match Over 9.5 Corners"
- "Match Over 4.5 Cards"
- "Over 2.5 Goals"
- "Both Teams To Score - Yes"
- "Bruno Fernandes Anytime Goalscorer"
- "Bruno Fernandes To Be Booked"

❌ **INCORRECT:**
- ~~"Manchester United Over 5.5 Corners"~~ (team-specific, not match total)
- ~~"Team Cards Over 2.5"~~ (not match total)
- ~~"Bruno Fernandes Goal"~~ (not proper market name)

### 8. Time Formats

**Different time formats in different fields:**

```python
# Unix timestamp (integer)
match['date_unix']  # 1758385800

# Goal/card times (string)
match['homeGoals']  # ["14", "37", "45+2"]

# Substitution times (string with apostrophe)
sub['player_out_time']  # "69'" or "-1"
```

### 9. File Path Examples

```
# League data
data/leagues/england_premier_league_15050/metadata.json
data/leagues/england_premier_league_15050/league_table.json
data/leagues/england_premier_league_15050/matches/8223489.json
data/leagues/england_premier_league_15050/match_details/8223489.json

# Team data
data/teams/Manchester_United_149/team_info.json
data/teams/Manchester_United_149/all_fixtures.json
data/teams/Manchester_United_149/all_stats.json

# Player data
data/leagues/england_premier_league_15050/players/464625.json
data/leagues/england_premier_league_15050/players/18226.json

# H2H data
data/leagues/england_premier_league_15050/h2h/149_vs_152.json
```

### 10. Common Pitfalls to Avoid

❌ **DON'T:**
- Use `homeCorners` instead of `team_a_corners`
- Include future gameweeks in backtest training data
- Use incomplete matches in statistics
- Predict team-specific markets (e.g., "Man Utd Over 5.5 Corners")
- Ignore data quality indicators
- Skip player ID to name mapping for validation

✅ **DO:**
- Always use `team_a_*` and `team_b_*` for stats
- Filter by `game_week < target_gameweek` for backtesting
- Filter by `status == "complete"`
- Predict match-level totals (e.g., "Match Over 9.5 Corners")
- Check recording indicators before using stats
- Use PlayerMapper for player validation

---

## Quick Reference: Most Important Fields

### For Match Predictions:
- `team_a_corners` / `team_b_corners`
- `team_a_cards_num` / `team_b_cards_num`
- `team_a_shots` / `team_b_shots`
- `totalGoalCount`
- `btts`

### For Validation:
- `lineups.team_a[].player_id`
- `lineups.team_a[].player_events`
- `team_a_goal_details[].player_id`
- `team_a_card_details[].player_id`

### For Filtering:
- `game_week`
- `status`
- `_league_key`
- `_season_id`
- `competition_id`

### For Quality Checks:
- `corner_timings_recorded`
- `card_timings_recorded`
- `attacks_recorded`
- `goal_timings_recorded`

---

**END OF DOCUMENTATION**

This documentation is comprehensive and covers every field, file path, and critical implementation detail needed for the football betting analysis system.