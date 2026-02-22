"""
Collector for global stats (BTTS, Over 2.5)
"""

from ..api_client import APIClient
from ..data_manager import GlobalDataManager


class StatsCollector:
    """
    Collects global statistics (BTTS, Over 2.5)
    """
    
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
    
    def collect_btts_stats(self) -> bool:
        """
        Collect BTTS statistics
        
        Returns:
            True if successful, False otherwise
        """
        print("  Fetching BTTS stats...")
        
        response = self.api_client.get_btts_stats()
        
        if not response or not response.get('success'):
            print("  ✗ Failed to fetch BTTS stats")
            return False
        
        # Save data
        GlobalDataManager.save_btts_stats(response)
        print("  ✓ BTTS stats saved")
        
        return True
    
    def collect_over25_stats(self) -> bool:
        """
        Collect Over 2.5 statistics
        
        Returns:
            True if successful, False otherwise
        """
        print("  Fetching Over 2.5 stats...")
        
        response = self.api_client.get_over25_stats()
        
        if not response or not response.get('success'):
            print("  ✗ Failed to fetch Over 2.5 stats")
            return False
        
        # Save data
        GlobalDataManager.save_over25_stats(response)
        print("  ✓ Over 2.5 stats saved")
        
        return True
    
    def collect_all(self) -> bool:
        """
        Collect all global stats
        
        Returns:
            True if all successful, False otherwise
        """
        print("\n📈 Collecting global stats...")
        
        btts_ok = self.collect_btts_stats()
        over25_ok = self.collect_over25_stats()
        
        return btts_ok and over25_ok