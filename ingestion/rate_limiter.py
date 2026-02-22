"""
Rate limiter to handle 1800 requests per hour limit
"""

import time
import json
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from .config import REQUESTS_PER_HOUR, STATE_DIR


class RateLimiter:
    """
    Manages API rate limiting (1800 requests per hour)
    Tracks calls and enforces waiting when limit is reached
    """
    
    STATE_FILE = STATE_DIR / "rate_limiter_state.json"
    
    def __init__(self, requests_per_hour: int = REQUESTS_PER_HOUR):
        self.requests_per_hour = requests_per_hour
        self.current_hour_start = None
        self.calls_this_hour = 0
        self.load_state()
    
    def load_state(self):
        """Load rate limiter state from disk"""
        if self.STATE_FILE.exists():
            try:
                with open(self.STATE_FILE, 'r') as f:
                    state = json.load(f)
                    
                    # Parse the hour start time
                    hour_start_str = state.get('current_hour_start')
                    if hour_start_str:
                        self.current_hour_start = datetime.fromisoformat(hour_start_str)
                    
                    # Check if we're still in the same hour
                    if self.current_hour_start and datetime.now() < self.current_hour_start + timedelta(hours=1):
                        self.calls_this_hour = state.get('calls_this_hour', 0)
                    else:
                        # New hour, reset
                        self.reset_hour()
            except Exception as e:
                print(f"⚠ Could not load rate limiter state: {e}")
                self.reset_hour()
        else:
            self.reset_hour()
    
    def save_state(self):
        """Save rate limiter state to disk"""
        state = {
            'current_hour_start': self.current_hour_start.isoformat() if self.current_hour_start else None,
            'calls_this_hour': self.calls_this_hour,
            'requests_per_hour': self.requests_per_hour
        }
        
        try:
            with open(self.STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save rate limiter state: {e}")
    
    def reset_hour(self):
        """Reset the hour counter"""
        self.current_hour_start = datetime.now()
        self.calls_this_hour = 0
        self.save_state()
    
    def can_make_request(self) -> bool:
        """
        Check if we can make a request without hitting the rate limit
        
        Returns:
            True if we can make a request, False otherwise
        """
        # Check if we need to reset the hour
        if not self.current_hour_start or datetime.now() >= self.current_hour_start + timedelta(hours=1):
            self.reset_hour()
            return True
        
        # Check if we're under the limit
        return self.calls_this_hour < self.requests_per_hour
    
    def wait_if_needed(self) -> Optional[int]:
        """
        Wait if rate limit has been reached
        
        Returns:
            Number of seconds waited, or None if no wait was needed
        """
        if self.can_make_request():
            return None
        
        # Calculate time until next hour
        next_hour = self.current_hour_start + timedelta(hours=1)
        wait_seconds = int((next_hour - datetime.now()).total_seconds()) + 1
        
        if wait_seconds > 0:
            print(f"\n⏸ Rate limit reached ({self.calls_this_hour}/{self.requests_per_hour} calls)")
            print(f"⏱ Waiting {wait_seconds} seconds until next hour...")
            print(f"⏰ Will resume at {next_hour.strftime('%H:%M:%S')}")
            
            time.sleep(wait_seconds)
            self.reset_hour()
            
            return wait_seconds
        
        return None
    
    def record_request(self):
        """
        Record that a request was made
        Call this after each successful API request
        """
        # Check if we need to reset the hour
        if not self.current_hour_start or datetime.now() >= self.current_hour_start + timedelta(hours=1):
            self.reset_hour()
        
        self.calls_this_hour += 1
        self.save_state()
    
    def get_remaining_requests(self) -> int:
        """
        Get number of requests remaining in current hour
        
        Returns:
            Number of requests remaining
        """
        if not self.current_hour_start or datetime.now() >= self.current_hour_start + timedelta(hours=1):
            return self.requests_per_hour
        
        return max(0, self.requests_per_hour - self.calls_this_hour)
    
    def get_status(self) -> dict:
        """
        Get current rate limiter status
        
        Returns:
            Dict with status information
        """
        if not self.current_hour_start:
            self.reset_hour()
        
        next_reset = self.current_hour_start + timedelta(hours=1)
        time_until_reset = (next_reset - datetime.now()).total_seconds()
        
        return {
            'calls_this_hour': self.calls_this_hour,
            'requests_per_hour': self.requests_per_hour,
            'remaining_requests': self.get_remaining_requests(),
            'hour_start': self.current_hour_start.isoformat(),
            'next_reset': next_reset.isoformat(),
            'seconds_until_reset': max(0, int(time_until_reset))
        }
    
    def print_status(self):
        """Print current rate limiter status"""
        status = self.get_status()
        print(f"\n📊 Rate Limit Status:")
        print(f"   Used: {status['calls_this_hour']}/{status['requests_per_hour']}")
        print(f"   Remaining: {status['remaining_requests']}")
        print(f"   Resets in: {status['seconds_until_reset']} seconds")