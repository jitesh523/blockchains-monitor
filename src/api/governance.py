import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
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
            "variables": {"space": space}
        }

        async with httpx.AsyncClient() as client:
            for _ in range(3):  # Retry logic
                try:
                    response = await client.post(SNAPSHOT_GRAPHQL_ENDPOINT, json=query)
                    if response.status_code == 200:
                        data = response.json()
                        return data.get("data", {}).get("proposals", [])
                except httpx.HTTPStatusError as e:
                    logger.error(f"Snapshot API error: {e}")
                await asyncio.sleep(1)
        return []

    async def fetch_tally_proposals(self, organization: str) -> List[Dict[str, Any]]:
        """Fetch recent proposals from Tally for a given organization."""
        url = f"{TALLY_API_ENDPOINT}/proposals?orgId={organization}&limit=5"

        async with httpx.AsyncClient() as client:
            for _ in range(3):
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        return response.json().get("data", [])
                except httpx.HTTPStatusError as e:
                    logger.error(f"Tally API error: {e}")
                await asyncio.sleep(1)
        return []

    def normalize_snapshot_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Snapshot proposal data."""
        return {
            "title": proposal.get("title", "Unknown"),
            "status": proposal.get("state", "Unknown"),
            "created": datetime.fromtimestamp(proposal.get("start", 0)),
            "votes": proposal.get("scores_total", 0)
        }

    def normalize_tally_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Tally proposal data."""
        return {
            "title": proposal.get("title", "Unknown"),
            "status": proposal.get("status", "Unknown"),
            "created": datetime.fromisoformat(proposal.get("created")),
            "votes": proposal.get("totalVotes", 0)
        }

    async def log_latest_proposals(self, space: str, organization: str):
        """Log a summary of latest proposals from both Snapshot and Tally."""
        snapshot_proposals = await self.fetch_snapshot_proposals(space)
        tally_proposals = await self.fetch_tally_proposals(organization)

        all_proposals = (
            [self.normalize_snapshot_proposal(p) for p in snapshot_proposals] +
            [self.normalize_tally_proposal(p) for p in tally_proposals]
        )

        for proposal in all_proposals:
            logger.info(
                f"Title: {proposal['title']}, Status: {proposal['status']}, "
                f"Created: {proposal['created']}, Votes: {proposal['votes']}"
            )
