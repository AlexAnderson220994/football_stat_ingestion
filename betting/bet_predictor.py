"""
Bet Predictor - BALANCED
Find the sweet spot: high confidence + good value
"""

from typing import Dict, List, Optional


class BetPredictor:
    """
    Generates betting predictions for markets actually offered by bet365
    ONE prediction per market type - highest confidence with decent value
    """
    
    def __init__(self):
        self.ultra_safe_threshold = 90
        self.safe_threshold = 75
        self.risky_threshold = 60
    
    def predict_match_corners(self, home_avg: float, away_avg: float, 
                             matches_played: int, h2h_avg: Optional[float] = None) -> List[Dict]:
        """
        Predict MATCH total corners - find sweet spot between certainty and value
        Target: Lines that are 90%+ likely but still offer decent odds (1.3-2.0)
        """
        if matches_played < 3:
            return []
        
        match_avg = home_avg + away_avg
        
        # Find best line in the "sweet spot"
        best_prediction = None
        best_confidence = 0
        
        # (line, base_conf, odds, direction, buffer_needed)
        # Sweet spot: lines between 5.5 and 11.5 corners
        options = [
            # OVERS - sweet spot for value
            (5.5, 96, 1.15, 'over', 2.5),   # avg > 8.0 = 96% confident
            (6.5, 94, 1.25, 'over', 2.0),   # avg > 8.5 = 94% confident
            (7.5, 91, 1.40, 'over', 2.0),   # avg > 9.5 = 91% confident
            (8.5, 88, 1.50, 'over', 1.5),   # avg > 10.0 = 88% confident
            (9.5, 84, 1.70, 'over', 1.5),   # avg > 11.0 = 84% confident
            (10.5, 79, 1.90, 'over', 1.5),  # avg > 12.0 = 79% confident
            (11.5, 73, 2.10, 'over', 1.5),  # avg > 13.0 = 73% confident
            
            # UNDERS - for low-scoring matches
            (13.5, 91, 1.40, 'under', -2.0), # avg < 11.5 = 91% confident
            (12.5, 86, 1.60, 'under', -1.5), # avg < 11.0 = 86% confident
            (11.5, 80, 1.83, 'under', -1.5), # avg < 10.0 = 80% confident
        ]
        
        for line, base_conf, odds, direction, buffer in options:
            if direction == 'over':
                if match_avg > (line + buffer):
                    confidence = base_conf
                else:
                    continue
            else:
                if match_avg < (line + buffer):
                    confidence = base_conf
                else:
                    continue
            
            # Take the highest confidence option
            if confidence > best_confidence:
                best_confidence = confidence
                best_prediction = {
                    'market': f'Match {direction.title()} {line} Corners',
                    'selection': f'{direction.title()} {line}',
                    'line': line,
                    'confidence': confidence,
                    'avg': match_avg,
                    'odds': odds,
                    'category': self._get_category(confidence),
                    'bet365_market': 'Corners',
                    'type': 'match'
                }
        
        return [best_prediction] if best_prediction else []
    
    def predict_match_cards(self, home_avg: float, away_avg: float, 
                           matches_played: int) -> List[Dict]:
        """
        Predict MATCH total cards - sweet spot between certainty and value
        Target: 90%+ confidence with odds 1.3-2.0
        """
        if matches_played < 3:
            return []
        
        match_avg = home_avg + away_avg
        
        best_prediction = None
        best_confidence = 0
        
        # Sweet spot: lines between 1.5 and 5.5 cards
        options = [
            # OVERS
            (1.5, 96, 1.10, 'over', 1.0),   # avg > 2.5 = 96% confident
            (2.5, 92, 1.40, 'over', 0.8),   # avg > 3.3 = 92% confident
            (3.5, 87, 1.75, 'over', 0.7),   # avg > 4.2 = 87% confident
            (4.5, 79, 2.00, 'over', 0.7),   # avg > 5.2 = 79% confident
            (5.5, 70, 2.40, 'over', 0.7),   # avg > 6.2 = 70% confident
            
            # UNDERS
            (6.5, 91, 1.40, 'under', -1.0), # avg < 5.5 = 91% confident
            (5.5, 84, 1.70, 'under', -0.7), # avg < 4.8 = 84% confident
        ]
        
        for line, base_conf, odds, direction, buffer in options:
            if direction == 'over':
                if match_avg > (line + buffer):
                    confidence = base_conf
                else:
                    continue
            else:
                if match_avg < (line + buffer):
                    confidence = base_conf
                else:
                    continue
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_prediction = {
                    'market': f'Match {direction.title()} {line} Cards',
                    'selection': f'{direction.title()} {line}',
                    'line': line,
                    'confidence': confidence,
                    'avg': match_avg,
                    'odds': odds,
                    'category': self._get_category(confidence),
                    'bet365_market': 'Cards',
                    'type': 'match'
                }
        
        return [best_prediction] if best_prediction else []
    
    def predict_match_goals(self, expected_goals: float, btts_pct_avg: float, 
                           matches_played: int) -> List[Dict]:
        """
        Predict goal markets - sweet spot between certainty and value
        """
        if matches_played < 3:
            return []
        
        predictions = []
        
        # Find best over/under line
        best_prediction = None
        best_confidence = 0
        
        # Sweet spot: lines between 1.5 and 3.5 goals
        options = [
            # OVERS
            (1.5, 93, 1.25, 'over', 0.6),   # avg > 2.1 = 93% confident
            (2.5, 84, 1.67, 'over', 0.6),   # avg > 3.1 = 84% confident
            (3.5, 71, 2.40, 'over', 0.6),   # avg > 4.1 = 71% confident
            
            # UNDERS
            (4.5, 91, 1.33, 'under', -1.0), # avg < 3.5 = 91% confident
            (3.5, 82, 1.67, 'under', -0.6), # avg < 2.9 = 82% confident
            (2.5, 68, 2.20, 'under', -0.4), # avg < 2.1 = 68% confident
        ]
        
        for line, base_conf, odds, direction, buffer in options:
            if direction == 'over':
                if expected_goals > (line + buffer):
                    confidence = base_conf
                else:
                    continue
            else:
                if expected_goals < (line + buffer):
                    confidence = base_conf
                else:
                    continue
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_prediction = {
                    'market': f'{direction.title()} {line} Goals',
                    'selection': f'{direction.title()} {line}',
                    'line': line,
                    'confidence': confidence,
                    'expected': round(expected_goals, 1),
                    'odds': odds,
                    'category': self._get_category(confidence),
                    'bet365_market': 'Goals Over/Under',
                    'type': 'match'
                }
        
        if best_prediction:
            predictions.append(best_prediction)
        
        # BTTS - separate prediction
        if btts_pct_avg > 65:
            confidence = min(int(btts_pct_avg * 1.30), 95)
            predictions.append({
                'market': 'Both Teams To Score - Yes',
                'selection': 'Yes',
                'confidence': confidence,
                'btts_pct': round(btts_pct_avg, 1),
                'odds': 1.70,
                'category': self._get_category(confidence),
                'bet365_market': 'Both Teams To Score',
                'type': 'match'
            })
        elif btts_pct_avg < 35:
            confidence = min(int((100 - btts_pct_avg) * 1.35), 95)
            predictions.append({
                'market': 'Both Teams To Score - No',
                'selection': 'No',
                'confidence': confidence,
                'btts_pct': round(btts_pct_avg, 1),
                'odds': 2.00,
                'category': self._get_category(confidence),
                'bet365_market': 'Both Teams To Score',
                'type': 'match'
            })
        
        return predictions
    
    def predict_player_card(self, player_name: str, cards_per_90: float, 
                          minutes: int, position: str) -> Optional[Dict]:
        """Predict player to be booked - PLAYER PROP"""
        if minutes < 450:
            return None
        
        # Position boost
        position_multiplier = 1.0
        if 'Defender' in position or 'Back' in position:
            position_multiplier = 1.12
        elif 'Midfielder' in position:
            position_multiplier = 1.06
        
        # Base confidence from card rate
        if cards_per_90 >= 0.50:
            base_confidence = 75
            odds = 2.75
        elif cards_per_90 >= 0.40:
            base_confidence = 70
            odds = 3.00
        elif cards_per_90 >= 0.32:
            base_confidence = 65
            odds = 3.50
        else:
            return None
        
        # Minutes multiplier (minimal)
        if minutes >= 1350:
            minutes_mult = 1.00
        elif minutes >= 900:
            minutes_mult = 0.97
        else:
            minutes_mult = 0.93
        
        confidence = int(base_confidence * position_multiplier * minutes_mult)
        
        if confidence < 60:  # Lower threshold for player props
            return None
        
        return {
            'market': f'{player_name} To Be Booked',
            'selection': player_name,
            'player': player_name,
            'confidence': confidence,
            'cards_per_90': cards_per_90,
            'position': position,
            'odds': odds,
            'category': 'player',  # Special category
            'bet365_market': 'Player Cards',
            'type': 'player'
        }
    
    def predict_player_goal(self, player_name: str, goals_per_90: float, 
                          minutes: int) -> Optional[Dict]:
        """Predict player anytime goalscorer - PLAYER PROP"""
        if minutes < 450:
            return None
        
        if goals_per_90 >= 0.75:
            base_confidence = 78
            odds = 1.90
        elif goals_per_90 >= 0.60:
            base_confidence = 73
            odds = 2.30
        elif goals_per_90 >= 0.45:
            base_confidence = 66
            odds = 2.70
        else:
            return None
        
        # Minutes multiplier
        if minutes >= 1350:
            minutes_mult = 1.00
        elif minutes >= 900:
            minutes_mult = 0.97
        else:
            minutes_mult = 0.93
        
        confidence = int(base_confidence * minutes_mult)
        
        if confidence < 60:
            return None
        
        return {
            'market': f'{player_name} Anytime Goalscorer',
            'selection': player_name,
            'player': player_name,
            'confidence': confidence,
            'goals_per_90': goals_per_90,
            'odds': odds,
            'category': 'player',  # Special category
            'bet365_market': 'Goalscorer',
            'type': 'player'
        }
    
    def _get_category(self, confidence: int) -> str:
        """Get confidence category"""
        if confidence >= self.ultra_safe_threshold:
            return 'ultra_safe'
        elif confidence >= self.safe_threshold:
            return 'safe'
        elif confidence >= self.risky_threshold:
            return 'risky'
        else:
            return 'too_risky'
    
    def generate_bet_builders(self, all_predictions: Dict) -> List[Dict]:
        """
        Generate bet builder combinations
        ONLY use match markets (no player props)
        """
        builders = []
        
        # Only use match markets for builders
        ultra_safe = [p for p in all_predictions.get('ultra_safe', []) 
                     if p.get('type') == 'match']
        safe = [p for p in all_predictions.get('safe', []) 
               if p.get('type') == 'match']
        risky = [p for p in all_predictions.get('risky', []) 
                if p.get('type') == 'match']
        
        # Evens builder - 2 ultra safe
        if len(ultra_safe) >= 2:
            sorted_ultra = sorted(ultra_safe, key=lambda x: x['confidence'], reverse=True)
            bet1, bet2 = sorted_ultra[0], sorted_ultra[1]
            
            combined_odds = bet1['odds'] * bet2['odds']
            
            if 1.8 <= combined_odds <= 2.5:
                builders.append({
                    'name': 'EVENS BUILDER',
                    'target_odds': '1.8-2.2',
                    'selections': [bet1, bet2],
                    'combined_odds': round(combined_odds, 2),
                    'min_confidence': min(bet1['confidence'], bet2['confidence'])
                })
        
        # 2/1 builder - 2 ultra safe + 1 safe
        if len(ultra_safe) >= 2 and len(safe) >= 1:
            sorted_ultra = sorted(ultra_safe, key=lambda x: x['confidence'], reverse=True)
            sorted_safe = sorted(safe, key=lambda x: x['confidence'], reverse=True)
            
            bet1, bet2 = sorted_ultra[0], sorted_ultra[1]
            bet3 = sorted_safe[0]
            
            combined_odds = bet1['odds'] * bet2['odds'] * bet3['odds']
            
            if 2.5 <= combined_odds <= 4.0:
                builders.append({
                    'name': '2/1 BUILDER',
                    'target_odds': '2.5-3.5',
                    'selections': [bet1, bet2, bet3],
                    'combined_odds': round(combined_odds, 2),
                    'min_confidence': min(bet1['confidence'], bet2['confidence'], bet3['confidence'])
                })
        
        # 3/1 builder - 1 ultra + 1 safe + 1 risky
        if len(ultra_safe) >= 1 and len(safe) >= 1 and len(risky) >= 1:
            sorted_ultra = sorted(ultra_safe, key=lambda x: x['confidence'], reverse=True)
            sorted_safe = sorted(safe, key=lambda x: x['confidence'], reverse=True)
            sorted_risky = sorted(risky, key=lambda x: x['confidence'], reverse=True)
            
            bet1 = sorted_ultra[0]
            bet2 = sorted_safe[0]
            bet3 = sorted_risky[0]
            
            combined_odds = bet1['odds'] * bet2['odds'] * bet3['odds']
            
            if 3.5 <= combined_odds <= 5.5:
                builders.append({
                    'name': '3/1 BUILDER',
                    'target_odds': '3.5-4.5',
                    'selections': [bet1, bet2, bet3],
                    'combined_odds': round(combined_odds, 2),
                    'min_confidence': min(bet1['confidence'], bet2['confidence'], bet3['confidence'])
                })
        
        return builders