#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
test_tfl.py
-----------
Quick test for the TfL client. Fetches live arrivals at Canning Town
and prints them to stdout.

Run from the project root:
    TFL_API_KEY=your_key python src/test/test_tfl.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))

from tfl_client import TflClient, CANNING_TOWN_STOP_ID

def main():
    client = TflClient()

    print(f"\nFetching arrivals at Canning Town ({CANNING_TOWN_STOP_ID})...\n")
    arrivals = client.get_arrivals()

    if not arrivals:
        print("No arrivals returned. Check your API key or network connection.")
        return

    print(f"{'#':<4} {'Line':<10} {'Destination':<38} {'Platform':<16} {'Mins':>4}")
    print("-" * 76)
    for i, a in enumerate(arrivals, 1):
        dest = (
            a.destination
            .replace(" Underground Station", "")
            .replace(" DLR Station", "")
            .replace(" Rail Station", "")
        )
        mins = "Due" if a.minutes_away == 0 else f"{a.minutes_away}"
        print(f"{i:<4} {a.line_name:<10} {dest:<38} {a.platform:<16} {mins:>4}")

    print(f"\n{len(arrivals)} arrival(s) retrieved.")

if __name__ == "__main__":
    main()
