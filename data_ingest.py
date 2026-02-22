#!/usr/bin/env python3
"""
Football Stats Data Ingestion Script

Run this script to ingest data from the Football API.
Supports single league ingestion, bulk updates, and resuming interrupted ingestions.

Usage:
    python data_ingest.py
"""

import sys
from pathlib import Path

# Add ingestion directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ingestion.run_ingestion import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Ingestion interrupted by user")
        print("💾 Progress has been saved. Run again to resume.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)