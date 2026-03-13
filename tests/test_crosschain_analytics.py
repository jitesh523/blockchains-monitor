"""
Tests for crosschain_analytics.correlate_events().
"""

from datetime import datetime, timedelta, timezone

from src.analytics.crosschain_analytics import correlate_events


class TestCorrelateEvents:
    """Test suite for the cross-chain event correlation engine."""

    # ---- edge cases ----

    def test_empty_input(self):
        """correlate_events returns empty result for no events."""
        result = correlate_events([])
        assert result["clusters"] == []
        assert result["summary"]["total"] == 0
        assert result["summary"]["cross_chain"] == 0

    def test_single_event(self):
        """A single event produces one cluster with no cross-chain flag."""
        events = [{"upgrade": "X", "chain": "Ethereum", "timestamp": datetime.now(timezone.utc)}]
        result = correlate_events(events)
        assert result["summary"]["total"] == 1
        assert result["summary"]["cross_chain"] == 0
        cluster = result["clusters"][0]
        assert cluster["upgrade"] == "X"
        assert cluster["cross_chain"] is False

    # ---- core behaviour ----

    def test_cross_chain_detected(self, sample_crosschain_events):
        """Events on >=2 chains within the window are marked cross-chain."""
        result = correlate_events(sample_crosschain_events, window_minutes=60)
        cross_chain_clusters = [c for c in result["clusters"] if c["cross_chain"]]
        assert len(cross_chain_clusters) >= 1
        assert result["summary"]["cross_chain"] >= 1

    def test_single_chain_not_cross_chain(self, sample_single_chain_events):
        """Events on a single chain should not be marked cross-chain."""
        result = correlate_events(sample_single_chain_events, window_minutes=60)
        for cluster in result["clusters"]:
            assert cluster["cross_chain"] is False
        assert result["summary"]["cross_chain"] == 0

    def test_time_window_splits_buckets(self):
        """Events beyond the window boundary land in separate clusters."""
        now = datetime(2025, 1, 1, 12, 0, 0)
        events = [
            {"upgrade": "U1", "chain": "Ethereum", "timestamp": now},
            {"upgrade": "U1", "chain": "Polygon", "timestamp": now + timedelta(minutes=5)},
            # This event is beyond the 10-minute window
            {"upgrade": "U1", "chain": "Arbitrum", "timestamp": now + timedelta(minutes=20)},
        ]
        result = correlate_events(events, window_minutes=10)
        assert result["summary"]["total"] == 2  # two buckets

    def test_confidence_increases_with_cross_chain(self, sample_crosschain_events):
        """Cross-chain clusters should have higher confidence than single-chain."""
        result = correlate_events(sample_crosschain_events, window_minutes=60)
        for cluster in result["clusters"]:
            if cluster["cross_chain"]:
                assert cluster["confidence"] >= 0.4  # at least the cross-chain bonus

    def test_cluster_fields_present(self, sample_crosschain_events):
        """Each cluster dict should contain all expected fields."""
        result = correlate_events(sample_crosschain_events, window_minutes=60)
        required_keys = {
            "upgrade",
            "chains",
            "count",
            "start_time",
            "end_time",
            "time_spread_sec",
            "cross_chain",
            "confidence",
            "sample_events",
        }
        for cluster in result["clusters"]:
            assert required_keys.issubset(cluster.keys())

    def test_min_chains_parameter(self, sample_crosschain_events):
        """Raising min_chains should reduce cross-chain count."""
        result_default = correlate_events(sample_crosschain_events, window_minutes=60, min_chains=2)
        result_strict = correlate_events(sample_crosschain_events, window_minutes=60, min_chains=5)
        assert result_strict["summary"]["cross_chain"] <= result_default["summary"]["cross_chain"]

    # ---- timestamp parsing ----

    def test_iso_string_timestamps(self):
        """Events with ISO-format string timestamps are parsed correctly."""
        events = [
            {"upgrade": "T1", "chain": "Ethereum", "timestamp": "2025-06-01T12:00:00"},
            {"upgrade": "T1", "chain": "Polygon", "timestamp": "2025-06-01T12:05:00"},
        ]
        result = correlate_events(events, window_minutes=60)
        assert result["summary"]["total"] == 1
        assert result["clusters"][0]["cross_chain"] is True

    def test_none_timestamps_handled(self):
        """Events without timestamps should not crash the engine."""
        events = [
            {"upgrade": "N1", "chain": "Ethereum"},
            {"upgrade": "N1", "chain": "Polygon"},
        ]
        result = correlate_events(events, window_minutes=60)
        assert result["summary"]["total"] >= 1
