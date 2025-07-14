import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta
from src.api.governance import GovernanceClient
from src.models.volatility_model import get_protocol_volatility
from src.models.sentiment_model import get_sentiment_for_protocol, categorize_sentiment, get_sentiment_color, analyze_sentiment
from src.models.liquidity_model import get_tvl_history, forecast_tvl
import logging

logger = logging.getLogger(__name__)

async def fetch_and_display_proposals(g_client: GovernanceClient, space: str, organization: str):
    """Fetch proposals and display on a timeline using Plotly and Streamlit."""
    # Mock sentiment data
    mock_tweets_map = {
        "Uniswap": [
            "This proposal looks solid!",
            "Gov vote might shift liquidity.",
            "Could be risky in the short term."
        ],
        "Aave": [
            "No major changes, good stability.",
            "I'm bullish on this proposal.",
            "This vote is a game changer!"
        ]
    }

    try:
        with st.spinner("Fetching proposals..."):
            # Fetch proposals from both sources
            snapshot_proposals = await g_client.fetch_snapshot_proposals(space) if space else []
            tally_proposals = await g_client.fetch_tally_proposals(organization) if organization else []
            
            all_proposals = []
            
            # Process Snapshot proposals
            for proposal in snapshot_proposals:
                norm_prop = g_client.normalize_snapshot_proposal(proposal)
                norm_prop['source'] = 'Snapshot'
                norm_prop['protocol'] = space
                tweets = mock_tweets_map.get(norm_prop['protocol'], ["Looks okay", "Neutral proposal", "Minor upgrade."])
                norm_prop['sentiment_score'] = analyze_sentiment(tweets)
                all_proposals.append(norm_prop)
            
            # Process Tally proposals
            for proposal in tally_proposals:
                norm_prop = g_client.normalize_tally_proposal(proposal)
                norm_prop['source'] = 'Tally'
                norm_prop['protocol'] = organization
                tweets = mock_tweets_map.get(norm_prop['protocol'], ["Looks okay", "Neutral proposal", "Minor upgrade."])
                norm_prop['sentiment_score'] = analyze_sentiment(tweets)
                all_proposals.append(norm_prop)
            
            if not all_proposals:
                st.warning("No proposals found for the specified space/organization.")
                return
            
            # Sort by creation date
            all_proposals.sort(key=lambda x: x['created'], reverse=True)
            
            # Create timeline visualization
            create_timeline_chart(all_proposals)
            
            # Create detailed proposal table
            create_proposal_table(all_proposals)
            
    except Exception as e:
        st.error(f"Error fetching proposals: {str(e)}")
        logger.error(f"Error in fetch_and_display_proposals: {e}")

def create_timeline_chart(proposals):
    """Create an interactive timeline chart of proposals."""
    if not proposals:
        return
    
    # Prepare data for timeline
    df_data = []
    for i, prop in enumerate(proposals):
        df_data.append({
            'Task': f"{prop['title'][:50]}{'...' if len(prop['title']) > 50 else ''}",
            'Start': prop['created'],
            'Finish': prop['created'] + timedelta(hours=1),  # Small duration for visibility
            'Status': prop['status'],
            'Source': prop['source'],
            'Protocol': prop['protocol'],
            'Votes': prop['votes'],
            'Full_Title': prop['title']
        })
    
    df = pd.DataFrame(df_data)
    
    # Create Gantt chart
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Status",
        hover_data=["Source", "Protocol", "Votes"],
        title="Protocol Upgrade Timeline",
        labels={"Task": "Proposal Title"},
        color_discrete_map={
            'active': '#28a745',
            'executed': '#17a2b8', 
            'failed': '#dc3545',
            'pending': '#ffc107',
            'closed': '#6c757d'
        }
    )
    
    fig.update_layout(
        height=max(400, len(proposals) * 30),
        showlegend=True,
        xaxis_title="Timeline",
        yaxis_title="Proposals"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_proposal_table(proposals):
    """Create a detailed table of proposals with voting progress and volatility."""
    st.subheader("Proposal Details")
    
    # Create columns for the table
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([3, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    
    with col1:
        st.write("**Title**")
    with col2:
        st.write("**Protocol**")
    with col3:
        st.write("**Status**")
    with col4:
        st.write("**Created**")
    with col5:
        st.write("**Volatility**")
    with col6:
        st.write("**Sentiment API**")
    with col7:
        st.write("**Sentiment Mock**")
    with col8:
        st.write("**Sentiment API**")
    with col9:
        st.write("**TVL Forecast**")
    with col10:
        st.write("**Votes**")
    
    st.divider()
    
    # Initialize caches in session state
    if 'volatility_cache' not in st.session_state:
        st.session_state.volatility_cache = {}
    if 'sentiment_cache' not in st.session_state:
        st.session_state.sentiment_cache = {}
    
    for prop in proposals:
        col1, col2, col3, col4, col5, col6, col7, col8, col9, col10 = st.columns([3, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        
        with col1:
            st.write(prop['title'])
        
        with col2:
            st.write(prop['protocol'])
        
        with col3:
            status_color = {
                'active': '🟢',
                'executed': '🔵',
                'failed': '🔴',
                'pending': '🟡',
                'closed': '⚫'
            }.get(prop['status'].lower(), '⚪')
            st.write(f"{status_color} {prop['status']}")
        
        with col4:
            st.write(prop['created'].strftime("%m/%d/%Y"))
        
        with col5:
            # Volatility forecast
            protocol_name = prop['protocol']
            if protocol_name not in st.session_state.volatility_cache:
                try:
                    # Run async function in sync context
                    vol_data = asyncio.run(get_protocol_volatility(protocol_name))
                    st.session_state.volatility_cache[protocol_name] = vol_data
                except Exception as e:
                    st.session_state.volatility_cache[protocol_name] = {'volatility': np.nan, 'error': str(e)}
            
            vol_info = st.session_state.volatility_cache[protocol_name]
            volatility = vol_info.get('volatility', np.nan)
            
            if not np.isnan(volatility):
                # Color code volatility: green (low), yellow (medium), red (high)
                if volatility < 30:
                    vol_color = "🟢"
                elif volatility < 60:
                    vol_color = "🟡"
                else:
                    vol_color = "🔴"
                st.write(f"{vol_color} {volatility:.1f}%")
            else:
                st.write("⚪ N/A")
        
        with col6:
            # Sentiment analysis
            if protocol_name not in st.session_state.sentiment_cache:
                try:
                    # Get sentiment for the protocol
                    sentiment_data = get_sentiment_for_protocol(protocol_name)
                    st.session_state.sentiment_cache[protocol_name] = sentiment_data
                except Exception as e:
                    st.session_state.sentiment_cache[protocol_name] = {'average_sentiment': 0.0, 'error': str(e)}

            sentiment_info = st.session_state.sentiment_cache[protocol_name]
            sent_score = sentiment_info.get('average_sentiment', 0.0)
            sent_color = get_sentiment_color(sent_score)
            sentiment_category = categorize_sentiment(sent_score)
            
            st.write(f"{sent_color} {sentiment_category}")

        with col7:
            # Sentiment score (Mock)
            sentiment = prop.get('sentiment_score', 0)
            if sentiment > 0.3:
                sentiment_label = "😊 Positive"
            elif sentiment < -0.3:
                sentiment_label = "😠 Negative"
            else:
                sentiment_label = "😐 Neutral"
            st.metric(label="Sentiment (Mock)", value=sentiment_label, delta=f"{sentiment}")
        
        with col8:
            # Actual sentiment from an API
            # This represents a placeholder for real-time data integration
            # Replace this logic with proper function call to fetch actual sentiment
            actual_sentiment = prop.get('sentiment_score', 0)  # Replace with actual sentiment fetching logic
            true_label = "😊 Positive" if actual_sentiment > 0.3 else ("😠 Negative" if actual_sentiment < -0.3 else "😐 Neutral")        
            st.metric(label="Sentiment (API)", value=true_label, delta=f"{actual_sentiment}")
        
        with col9:
            # Forecast TVL
            protocol_slug = prop['protocol'].lower().replace(' ', '-')
            df_tvl = await get_tvl_history(protocol_slug)
            current_tvl = df_tvl['y'].iloc[-1]
            forecasted_tvl = forecast_tvl(df_tvl)
            delta_tvl = forecasted_tvl - current_tvl
            st.metric("TVL Forecast (7d)", f"${forecasted_tvl:,.2f}", delta=f"${delta_tvl:+,.2f}")

        with col10:
            # Create a simple voting progress bar
            votes = prop.get('votes', 0)
            if isinstance(votes, (int, float)) and votes > 0:
                st.metric("Total Votes", f"{votes:,.0f}")
            else:
                st.write("No vote data")
        
        st.divider()

def create_sidebar():
    """Create sidebar with configuration options."""
    st.sidebar.header("Configuration")
    
    # Network selection
    network = st.sidebar.selectbox(
        "Select Network",
        ["Ethereum", "Polygon", "Arbitrum", "All Networks"]
    )
    
    # Time filter
    time_filter = st.sidebar.selectbox(
        "Time Range",
        ["Last 24 hours", "Last 7 days", "Last 30 days", "All time"]
    )
    
    # Status filter
    status_filter = st.sidebar.multiselect(
        "Filter by Status",
        ["active", "executed", "failed", "pending", "closed"],
        default=["active", "executed", "pending"]
    )
    
    return network, time_filter, status_filter

async def main():
    st.set_page_config(
        page_title="Protocol Upgrade Monitor",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔗 Blockchain Protocol Upgrade Timeline")
    st.markdown(
        """Monitor and visualize recent protocol proposals from governance platforms like Snapshot and Tally.
        Get real-time insights into protocol upgrades and their potential impact on your portfolio."""
    )
    
    # Create sidebar
    network, time_filter, status_filter = create_sidebar()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Data Sources")
        space = st.text_input(
            "Snapshot Space ID:", 
            placeholder="e.g., uniswap, aave.eth, compound",
            help="Enter the Snapshot space identifier for the protocol"
        )
        
    with col2:
        st.subheader("🏛️ Governance Platform")
        organization = st.text_input(
            "Tally Organization:", 
            placeholder="e.g., compound, aave",
            help="Enter the Tally organization identifier"
        )
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        refresh_clicked = st.button("🔄 Refresh Timeline", type="primary")
    
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (30s)")
    
    # Auto-refresh logic
    if auto_refresh:
        st.rerun()
    
    # Fetch and display data
    if refresh_clicked or (space and organization):
        if not space and not organization:
            st.warning("Please enter at least one data source (Snapshot space or Tally organization).")
        else:
            g_client = GovernanceClient()
            await fetch_and_display_proposals(g_client, space, organization)
    
    # Display example spaces/organizations
    if not refresh_clicked:
        st.subheader("💡 Popular Protocols")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(
                "**Snapshot Spaces:**\n"
                "• uniswap\n"
                "• aave.eth\n"
                "• compound\n"
                "• ens.eth"
            )
        
        with col2:
            st.info(
                "**Tally Organizations:**\n"
                "• compound\n"
                "• aave\n"
                "• gitcoin\n"
                "• frax"
            )
        
        with col3:
            st.info(
                "**Features:**\n"
                "• Real-time proposal tracking\n"
                "• Interactive timeline\n"
                "• Voting progress monitoring\n"
                "• Risk assessment alerts"
            )

if __name__ == '__main__':
    asyncio.run(main())
