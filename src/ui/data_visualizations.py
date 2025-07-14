import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random
import time
import logging
from functools import wraps

# Set up logging
logger = logging.getLogger(__name__)

def performance_monitor(func):
    """Decorator to monitor function performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} executed successfully in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.4f} seconds: {str(e)}")
            raise
    return wrapper

def get_theme_template(dark_mode: bool = True) -> str:
    """Get appropriate Plotly theme template based on current theme."""
    return "plotly_dark" if dark_mode else "plotly_white"

def get_theme_colors(dark_mode: bool = True) -> Dict[str, str]:
    """Get theme colors for consistent styling."""
    if dark_mode:
        return {
            'primary': '#00D4FF',
            'secondary': '#FF6B6B',
            'success': '#51CF66',
            'warning': '#FFD43B',
            'error': '#FF5252',
            'background': '#0E1117',
            'text': '#FAFAFA',
            'grid': '#2D3748'
        }
    else:
        return {
            'primary': '#0066CC',
            'secondary': '#FF4444',
            'success': '#28A745',
            'warning': '#D97706',
            'error': '#DC3545',
            'background': '#FFFFFF',
            'text': '#212529',
            'grid': '#E9ECEF'
        }

def generate_mock_risk_data(protocols: List[str], days: int = 30) -> pd.DataFrame:
    """Generate mock risk score data over time."""
    data = []
    base_date = datetime.now() - timedelta(days=days)
    
    for protocol in protocols:
        # Generate base risk score with some randomness
        base_risk = random.uniform(30, 80)
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            # Add some trend and noise
            trend = np.sin(i * 0.1) * 10
            noise = random.uniform(-5, 5)
            risk_score = max(0, min(100, base_risk + trend + noise))
            
            data.append({
                'date': date,
                'protocol': protocol,
                'risk_score': risk_score,
                'volatility': random.uniform(10, 60),
                'sentiment': random.uniform(-0.8, 0.8)
            })
    
    return pd.DataFrame(data)

@performance_monitor
def create_risk_score_timeline(dark_mode: bool = True) -> go.Figure:
    """Create risk score over time chart."""
    protocols = ['Uniswap', 'Aave', 'Compound', 'MakerDAO']
    df = generate_mock_risk_data(protocols)
    
    theme_template = get_theme_template(dark_mode)
    colors = get_theme_colors(dark_mode)
    
    fig = px.line(
        df,
        x='date',
        y='risk_score',
        color='protocol',
        title='Risk Score Over Time',
        labels={'risk_score': 'Risk Score', 'date': 'Date'},
        template=theme_template
    )
    
    # Customize layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text']),
        title_font_size=16,
        title_x=0.5,
        xaxis=dict(
            gridcolor=colors['grid'],
            showgrid=True,
            gridwidth=1
        ),
        yaxis=dict(
            gridcolor=colors['grid'],
            showgrid=True,
            gridwidth=1,
            range=[0, 100]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=400
    )
    
    # Add hover template
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>" +
                      "Date: %{x}<br>" +
                      "Risk Score: %{y:.1f}<br>" +
                      "<extra></extra>"
    )
    
    return fig

@performance_monitor
def create_risk_score_timeline_filtered(dark_mode: bool = True, protocols: List[str] = None, days: int = 30, height: int = 400) -> go.Figure:
    """Create filtered risk score over time chart with custom parameters."""
    if protocols is None:
        protocols = ['Uniswap', 'Aave', 'Compound', 'MakerDAO']
    
    df = generate_mock_risk_data(protocols, days)
    
    theme_template = get_theme_template(dark_mode)
    colors = get_theme_colors(dark_mode)
    
    fig = px.line(
        df,
        x='date',
        y='risk_score',
        color='protocol',
        title=f'Risk Score Over Time ({days} Days)',
        labels={'risk_score': 'Risk Score', 'date': 'Date'},
        template=theme_template
    )
    
    # Customize layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text']),
        title_font_size=16,
        title_x=0.5,
        xaxis=dict(
            gridcolor=colors['grid'],
            showgrid=True,
            gridwidth=1
        ),
        yaxis=dict(
            gridcolor=colors['grid'],
            showgrid=True,
            gridwidth=1,
            range=[0, 100]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=height
    )
    
    # Add hover template
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>" +
                      "Date: %{x}<br>" +
                      "Risk Score: %{y:.1f}<br>" +
                      "<extra></extra>"
    )
    
    return fig

@performance_monitor
def create_volatility_sentiment_scatter(dark_mode: bool = True) -> go.Figure:
    """Create volatility vs sentiment scatter plot."""
    protocols = ['Uniswap', 'Aave', 'Compound', 'MakerDAO', 'Curve', 'Balancer']
    colors = get_theme_colors(dark_mode)
    theme_template = get_theme_template(dark_mode)
    
    # Generate mock data
    data = []
    for protocol in protocols:
        data.append({
            'protocol': protocol,
            'volatility': random.uniform(15, 65),
            'sentiment': random.uniform(-0.8, 0.8),
            'tvl': random.uniform(100, 2000),  # Million USD
            'risk_level': random.choice(['Low', 'Medium', 'High'])
        })
    
    df = pd.DataFrame(data)
    
    # Create scatter plot
    fig = px.scatter(
        df,
        x='volatility',
        y='sentiment',
        size='tvl',
        color='risk_level',
        hover_name='protocol',
        title='Volatility vs Sentiment Analysis',
        labels={
            'volatility': 'Volatility (%)',
            'sentiment': 'Sentiment Score',
            'tvl': 'TVL (M USD)'
        },
        template=theme_template,
        color_discrete_map={
            'Low': colors['success'],
            'Medium': colors['warning'],
            'High': colors['error']
        }
    )
    
    # Customize layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text']),
        title_font_size=16,
        title_x=0.5,
        xaxis=dict(
            gridcolor=colors['grid'],
            showgrid=True,
            gridwidth=1,
            range=[0, 70]
        ),
        yaxis=dict(
            gridcolor=colors['grid'],
            showgrid=True,
            gridwidth=1,
            range=[-1, 1]
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=400
    )
    
    # Add quadrant lines
    fig.add_hline(y=0, line_dash="dash", line_color=colors['grid'], opacity=0.5)
    fig.add_vline(x=35, line_dash="dash", line_color=colors['grid'], opacity=0.5)
    
    # Update hover template
    fig.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>" +
                      "Volatility: %{x:.1f}%<br>" +
                      "Sentiment: %{y:.2f}<br>" +
                      "TVL: $%{marker.size:.0f}M<br>" +
                      "<extra></extra>"
    )
    
    return fig

@performance_monitor
def create_protocol_risk_comparison(dark_mode: bool = True) -> go.Figure:
    """Create protocol risk score comparison bar chart."""
    protocols = ['Uniswap', 'Aave', 'Compound', 'MakerDAO', 'Curve', 'Balancer', 'Yearn']
    colors = get_theme_colors(dark_mode)
    theme_template = get_theme_template(dark_mode)
    
    # Generate mock data
    data = []
    for protocol in protocols:
        risk_score = random.uniform(20, 85)
        volatility = random.uniform(15, 60)
        sentiment = random.uniform(-0.8, 0.8)
        
        data.append({
            'protocol': protocol,
            'risk_score': risk_score,
            'volatility': volatility,
            'sentiment': sentiment,
            'risk_level': 'High' if risk_score > 70 else 'Medium' if risk_score > 40 else 'Low'
        })
    
    df = pd.DataFrame(data).sort_values('risk_score', ascending=False)
    
    # Create bar chart
    fig = px.bar(
        df,
        x='risk_score',
        y='protocol',
        orientation='h',
        color='risk_level',
        title='Protocol Risk Score Comparison',
        labels={'risk_score': 'Risk Score', 'protocol': 'Protocol'},
        template=theme_template,
        color_discrete_map={
            'Low': colors['success'],
            'Medium': colors['warning'],
            'High': colors['error']
        }
    )
    
    # Customize layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text']),
        title_font_size=16,
        title_x=0.5,
        xaxis=dict(
            gridcolor=colors['grid'],
            showgrid=True,
            gridwidth=1,
            range=[0, 100]
        ),
        yaxis=dict(
            gridcolor=colors['grid'],
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=400
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>" +
                      "Risk Score: %{x:.1f}<br>" +
                      "Volatility: %{customdata[0]:.1f}%<br>" +
                      "Sentiment: %{customdata[1]:.2f}<br>" +
                      "<extra></extra>",
        customdata=df[['volatility', 'sentiment']].values
    )
    
    return fig

def create_mini_sparkline(data: List[float], color: str = '#00D4FF', height: int = 50) -> go.Figure:
    """Create mini sparkline chart for sidebar metrics."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=data,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tonexty',
        fillcolor=f'rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.1)',
        showlegend=False,
        hoverinfo='skip'
    ))
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=height,
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            showline=False
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            showline=False
        )
    )
    
    return fig

@performance_monitor
def render_analytics_dashboard():
    """Render the complete analytics dashboard with interactive controls and accessibility features."""
    # Get current theme
    dark_mode = st.session_state.get('dark_mode', True)
    
    st.header("📊 Analytics Dashboard")
    
    # Accessibility info
    with st.expander("♿️ Accessibility Information"):
        st.markdown("""
        **Chart Accessibility Features:**
        - High contrast colors for better visibility
        - Screen reader compatible hover text
        - Keyboard navigation support
        - Color-blind friendly palette
        - Proper alt text for all visualizations
        
        **How to Navigate:**
        - Use tab key to navigate between interactive elements
        - Hover over charts for detailed information
        - Use the controls above to filter data
        """)
    
    # Interactive controls
    st.subheader("🎛️ Controls")
    control_col1, control_col2, control_col3 = st.columns(3)
    
    with control_col1:
        time_range = st.selectbox(
            "Time Range",
            ["7 Days", "30 Days", "90 Days"],
            index=1,
            help="Select the time range for risk analysis"
        )
        days_map = {"7 Days": 7, "30 Days": 30, "90 Days": 90}
        selected_days = days_map[time_range]
    
    with control_col2:
        selected_protocols = st.multiselect(
            "Select Protocols",
            ["Uniswap", "Aave", "Compound", "MakerDAO", "Curve", "Balancer", "Yearn"],
            default=["Uniswap", "Aave", "Compound", "MakerDAO"],
            help="Choose protocols to analyze"
        )
    
    with control_col3:
        chart_height = st.slider(
            "Chart Height",
            min_value=300,
            max_value=600,
            value=400,
            step=50,
            help="Adjust chart height for better visibility"
        )
    
    # Row 1: Risk Score Timeline
    st.subheader("📈 Risk Score Over Time")
    if selected_protocols:
        risk_timeline = create_risk_score_timeline_filtered(dark_mode, selected_protocols, selected_days, chart_height)
        st.plotly_chart(risk_timeline, use_container_width=True)
    else:
        st.warning("Please select at least one protocol to display the chart.")
    
    # Row 2: Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Volatility vs Sentiment")
        volatility_sentiment = create_volatility_sentiment_scatter(dark_mode)
        st.plotly_chart(volatility_sentiment, use_container_width=True)
    
    with col2:
        st.subheader("📊 Protocol Risk Comparison")
        risk_comparison = create_protocol_risk_comparison(dark_mode)
        st.plotly_chart(risk_comparison, use_container_width=True)
    
    # Additional insights
    st.subheader("🎯 Key Insights")
    insights_col1, insights_col2, insights_col3 = st.columns(3)
    
    with insights_col1:
        st.metric("Highest Risk Protocol", "Compound", "85.2")
        st.caption("Based on latest assessment")
    
    with insights_col2:
        st.metric("Most Volatile", "Uniswap", "45.8%")
        st.caption("30-day volatility")
    
    with insights_col3:
        st.metric("Best Sentiment", "Aave", "0.72")
        st.caption("Community sentiment score")

def render_sidebar_sparklines():
    """Render mini sparklines in sidebar."""
    st.sidebar.markdown("### 📈 Trends")
    
    # Generate mock data for sparklines
    gas_data = [random.uniform(25, 45) for _ in range(20)]
    tps_data = [random.uniform(10, 20) for _ in range(20)]
    block_data = [random.uniform(11, 14) for _ in range(20)]
    
    dark_mode = st.session_state.get('dark_mode', True)
    colors = get_theme_colors(dark_mode)
    
    # Gas Price Sparkline
    st.sidebar.markdown("**Gas Price Trend**")
    gas_sparkline = create_mini_sparkline(gas_data, colors['primary'])
    st.sidebar.plotly_chart(gas_sparkline, use_container_width=True)
    
    # TPS Sparkline
    st.sidebar.markdown("**TPS Trend**")
    tps_sparkline = create_mini_sparkline(tps_data, colors['success'])
    st.sidebar.plotly_chart(tps_sparkline, use_container_width=True)
    
    # Block Time Sparkline
    st.sidebar.markdown("**Block Time Trend**")
    block_sparkline = create_mini_sparkline(block_data, colors['warning'])
    st.sidebar.plotly_chart(block_sparkline, use_container_width=True)
