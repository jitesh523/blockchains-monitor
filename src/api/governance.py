import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List

import httpx

logger = logging.getLogger(__name__)

SNAPSHOT_GRAPHQL_ENDPOINT = "https://hub.snapshot.org/graphql"
TALLY_API_ENDPOINT = "https://api.tally.xyz/v1"


class GovernanceClient:
    """Client for interacting with governance platforms like Snapshot and Tally."""

    async def fetch_snapshot_proposals(self, space: str) -> List[Dict[str, Any]]:
        """Fetch recent proposals from Snapshot for a given space."""
        query = {
            "query": """
            query Proposals($space: String!) {
                proposals(first: 5, where: {space: $space}, orderBy: "created", orderDirection: desc) {
                    id
                    title
                    start
                    end
                    state
                    scores
                    scores_total
                }
            }
            """,
            "variables": {"space": space},
        }

        # Use explicit timeout and exponential backoff
        async with httpx.AsyncClient(timeout=15.0) as client:
            for attempt in range(3):
                try:
                    response = await client.post(SNAPSHOT_GRAPHQL_ENDPOINT, json=query)
                    response.raise_for_status()
                    data = response.json()
                    return data.get("data", {}).get("proposals", [])
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    logger.warning(f"Snapshot API error (attempt {attempt + 1}/3): {e}")
                    await asyncio.sleep(2**attempt)
        return []

    async def fetch_tally_proposals(self, organization: str) -> List[Dict[str, Any]]:
        """Fetch recent proposals from Tally for a given organization."""
        url = f"{TALLY_API_ENDPOINT}/proposals?orgId={organization}&limit=5"

        headers = {}
        tally_api_key = os.getenv("TALLY_API_KEY")
        if tally_api_key:
            # Tally often expects a Bearer token
            headers["Authorization"] = f"Bearer {tally_api_key}"

        async with httpx.AsyncClient(timeout=15.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    return response.json().get("data", [])
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    logger.warning(f"Tally API error (attempt {attempt + 1}/3): {e}")
                    await asyncio.sleep(2**attempt)
        return []

    def normalize_snapshot_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Snapshot proposal data."""
        return {
            "title": proposal.get("title", "Unknown"),
            "status": proposal.get("state", "Unknown"),
            "created": datetime.fromtimestamp(proposal.get("start", 0)),
            "votes": proposal.get("scores_total", 0),
        }

    def normalize_tally_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Tally proposal data."""
        created_raw = proposal.get("created")
        created_dt: datetime
        try:
            created_dt = datetime.fromisoformat(created_raw) if created_raw else datetime.utcnow()
        except Exception:
            created_dt = datetime.utcnow()

        return {
            "title": proposal.get("title", "Unknown"),
            "status": proposal.get("status", "Unknown"),
            "created": created_dt,
            "votes": proposal.get("totalVotes", 0),
        }

    async def log_latest_proposals(self, space: str, organization: str):
        """Log a summary of latest proposals from both Snapshot and Tally."""
        snapshot_proposals = await self.fetch_snapshot_proposals(space)
        tally_proposals = await self.fetch_tally_proposals(organization)

        all_proposals = [self.normalize_snapshot_proposal(p) for p in snapshot_proposals] + [
            self.normalize_tally_proposal(p) for p in tally_proposals
        ]

        for proposal in all_proposals:
            logger.info(
                f"Title: {proposal['title']}, Status: {proposal['status']}, "
                f"Created: {proposal['created']}, Votes: {proposal['votes']}"
            )
