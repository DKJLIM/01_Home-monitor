#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
tfl_client.py
-------------
Fetches live train arrivals from the TfL Unified API.

Stop point IDs used:
    Canning Town (DLR/Jubilee): 940GZZLUCGT

Usage:
    Set the environment variable TFL_API_KEY to your TfL application key.
    Without a key the API still works but at a lower rate limit.

        export TFL_API_KEY="your_key_here"

    from modules.tfl_client import TflClient
    client = TflClient()
    arrivals = client.get_arrivals()
    for a in arrivals:
        print(a)
"""

import json
import logging
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import List, Optional

TFL_BASE_URL = "https://api.tfl.gov.uk"

# TfL stop-point NAPTAN codes
CANNING_TOWN_STOP_ID = "940GZZLUCGT"


@dataclass
class Arrival:
    """Represents a single train arrival at a stop."""
    line_name: str
    destination: str
    platform: str
    minutes_away: int
    vehicle_id: str = field(default="")

    def __str__(self) -> str:
        mins = "Due" if self.minutes_away == 0 else f"{self.minutes_away} min"
        return f"{self.line_name:<8}  {self.destination:<35}  {self.platform:<12}  {mins}"


class TflClient:
    """
    Thin wrapper around the TfL Unified API arrivals endpoint.

    Args:
        api_key: TfL application key. Falls back to the TFL_API_KEY
                 environment variable if not supplied.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("TFL_API_KEY", "")
        if not self.api_key:
            logging.warning(
                "No TFL_API_KEY set. Requests will be subject to a lower rate limit."
            )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_url(self, path: str) -> str:
        sep = "&" if "?" in path else "?"
        if self.api_key:
            return f"{TFL_BASE_URL}{path}{sep}app_key={self.api_key}"
        return f"{TFL_BASE_URL}{path}"

    def _get(self, path: str):
        url = self._build_url(path)
        headers = {
            "Cache-Control": "no-cache",
            "User-Agent": "HomeMonitor/1.0",
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_arrivals(
        self,
        stop_id: str = CANNING_TOWN_STOP_ID,
        max_results: int = 12,
    ) -> List[Arrival]:
        """
        Return upcoming arrivals at *stop_id*, sorted by arrival time.

        Args:
            stop_id: TfL NAPTAN stop-point code.
            max_results: Cap on number of arrivals returned.

        Returns:
            List of Arrival objects sorted by minutes_away (ascending).
            Returns an empty list on any API error.
        """
        try:
            data = self._get(f"/StopPoint/{stop_id}/Arrivals")
        except urllib.error.HTTPError as exc:
            logging.error("TfL API HTTP error: %s %s", exc.code, exc.reason)
            return []
        except Exception as exc:  # noqa: BLE001
            logging.error("TfL API request failed: %s", exc)
            return []

        arrivals: List[Arrival] = []
        for item in data:
            arrivals.append(
                Arrival(
                    line_name=item.get("lineName", ""),
                    destination=item.get("destinationName", "Unknown"),
                    platform=item.get("platformName", ""),
                    minutes_away=item.get("timeToStation", 0) // 60,
                    vehicle_id=item.get("vehicleId", ""),
                )
            )

        arrivals.sort(key=lambda a: a.minutes_away)
        return arrivals[:max_results]
