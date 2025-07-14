import pytest
import pandas as pd
import plotly.graph_objects as go
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.ui.data_visualizations import (
    get_theme_template,
    get_theme_colors,
    generate_mock_risk_data,
    create_risk_score_timeline,
    create_volatility_sentiment_scatter,
    create_protocol_risk_comparison,
    create_mini_sparkline
)

class TestDataVisualizations:
    """Test suite for data visualization functions."""

    def test_get_theme_template(self):
        """Test theme template selection."""
        assert get_theme_template(True) == "plotly_dark"
        assert get_theme_template(False) == "plotly_white"

    def test_get_theme_colors(self):
        """Test theme color retrieval."""
        dark_colors = get_theme_colors(True)
        light_colors = get_theme_colors(False)
        
        # Check that all required color keys exist
        required_keys = ['primary', 'secondary', 'success', 'warning', 'error', 'background', 'text', 'grid']
        for key in required_keys:
            assert key in dark_colors
            assert key in light_colors
        
        # Check that colors are different between themes
        assert dark_colors['background'] != light_colors['background']
        assert dark_colors['text'] != light_colors['text']

    def test_generate_mock_risk_data(self):
        """Test mock risk data generation."""
        protocols = ['Uniswap', 'Aave', 'Compound']
        df = generate_mock_risk_data(protocols, days=10)
        
        # Check DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(protocols) * 10
        
        # Check required columns
        required_columns = ['date', 'protocol', 'risk_score', 'volatility', 'sentiment']
        for col in required_columns:
            assert col in df.columns
        
        # Check data types and ranges
        assert df['risk_score'].min() >= 0
        assert df['risk_score'].max() <= 100
        assert df['volatility'].min() >= 0
        assert df['sentiment'].min() >= -1
        assert df['sentiment'].max() <= 1

    def test_create_risk_score_timeline(self):
        """Test risk score timeline chart creation."""
        fig = create_risk_score_timeline(dark_mode=True)
        
        # Check that it's a valid Plotly figure
        assert isinstance(fig, go.Figure)
        
        # Check that it has data
        assert len(fig.data) > 0
        
        # Check title
        assert 'Risk Score Over Time' in fig.layout.title.text

    def test_create_volatility_sentiment_scatter(self):
        """Test volatility vs sentiment scatter plot creation."""
        fig = create_volatility_sentiment_scatter(dark_mode=True)
        
        # Check that it's a valid Plotly figure
        assert isinstance(fig, go.Figure)
        
        # Check that it has data
        assert len(fig.data) > 0
        
        # Check title
        assert 'Volatility vs Sentiment Analysis' in fig.layout.title.text

    def test_create_protocol_risk_comparison(self):
        """Test protocol risk comparison bar chart creation."""
        fig = create_protocol_risk_comparison(dark_mode=True)
        
        # Check that it's a valid Plotly figure
        assert isinstance(fig, go.Figure)
        
        # Check that it has data
        assert len(fig.data) > 0
        
        # Check title
        assert 'Protocol Risk Score Comparison' in fig.layout.title.text

    def test_create_mini_sparkline(self):
        """Test mini sparkline chart creation."""
        data = [1, 2, 3, 4, 5, 4, 3, 2, 1]
        fig = create_mini_sparkline(data, color='#00D4FF', height=50)
        
        # Check that it's a valid Plotly figure
        assert isinstance(fig, go.Figure)
        
        # Check that it has data
        assert len(fig.data) > 0
        
        # Check height
        assert fig.layout.height == 50

    def test_theme_consistency(self):
        """Test that both themes produce valid charts."""
        # Test dark mode
        dark_fig = create_risk_score_timeline(dark_mode=True)
        assert isinstance(dark_fig, go.Figure)
        
        # Test light mode
        light_fig = create_risk_score_timeline(dark_mode=False)
        assert isinstance(light_fig, go.Figure)
        
        # Both should have same structure but different styling
        assert len(dark_fig.data) == len(light_fig.data)

if __name__ == "__main__":
    pytest.main([__file__])
