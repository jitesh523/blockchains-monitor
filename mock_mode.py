"""
mock_mode.py
Enable API mock/demo mode for offline demonstration.
"""
def mock_event_feed():
    # Returns dummy upgrade/risk events
    return [
        {"upgrade": "EIP-3333", "risk": "low", "chain": "Ethereum"},
        {"upgrade": "PolygonVote", "risk": "high", "chain": "Polygon"}
    ]

def mock_api_response(endpoint):
    # Dummy API outputs
    return {"endpoint": endpoint, "data": "sample_data"}

if __name__ == "__main__":
    print("[Mock Mode] Blockchain Events:", mock_event_feed())
    print("[Mock Mode] API Out:", mock_api_response("volatility"))

