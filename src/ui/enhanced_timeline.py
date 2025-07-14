import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any

from src.api.governance import GovernanceClient
from src.models.volatility_model import get_protocol_volatility
from src.models.sentiment_model import analyze_sentiment
from src.models.risk_model import get_risk_assessment
from src.ui.theme import (
    create_proposal_card, 
    create_network_status_card, 
    create_risk_indicator,
    create_loading_spinner
)

class EnhancedTimeline:
    """Enhanced timeline with modern UI components."""
    
    def __init__(self):
        self.mock_proposals = [
            {
                'title': 'Uniswap V4 Hooks Implementation',
                'protocol': 'Uniswap',
                'status': 'active',
                'created': '2024-01-15',
                'votes': 25000,
                'description': 'Implement hooks system for enhanced customization',
                'risk_factors': ['High complexity', 'Breaking changes']
            },
            {
                'title': 'Aave V3 Interest Rate Model Update',
                'protocol': 'Aave',
                'status': 'pending',
                'created': '2024-01-10',
                'votes': 18500,
                'description': 'Update interest rate calculations for better efficiency',
                'risk_factors': ['Market impact', 'Liquidation risks']
            },
            {
                'title': 'Compound Governance Token Migration',
                'protocol': 'Compound',
                'status': 'executed',
                'created': '2024-01-05',
                'votes': 32000,
                'description': 'Migrate to new governance token structure',
                'risk_factors': ['Token migration', 'Governance disruption']
            }
        ]
    
    async def render_timeline(self):
        """Render the enhanced timeline interface."""
        st.subheader("🔄 Protocol Upgrade Timeline")
        
        # Controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input("🔍 Search proposals...", placeholder="Search by title, protocol, or status")
        
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Pending", "Executed", "Failed"])
        
        with col3:
            sort_by = st.selectbox("Sort by", ["Date", "Risk Score", "Votes", "Protocol"])
        
        # Filter and sort proposals
        filtered_proposals = self._filter_proposals(self.mock_proposals, search_query, status_filter)
        sorted_proposals = self._sort_proposals(filtered_proposals, sort_by)
        
        # Display proposals
        if sorted_proposals:
            await self._render_proposal_cards(sorted_proposals)
        else:
            st.info("No proposals found matching your criteria.")
    
    def _filter_proposals(self, proposals: List[Dict], search_query: str, status_filter: str) -> List[Dict]:
        """Filter proposals based on search query and status."""
        filtered = proposals
        
        if search_query:
            filtered = [
                p for p in filtered 
                if search_query.lower() in p['title'].lower() or 
                   search_query.lower() in p['protocol'].lower() or 
                   search_query.lower() in p['status'].lower()
            ]
        
        if status_filter != "All":
            filtered = [p for p in filtered if p['status'].lower() == status_filter.lower()]
        
        return filtered
    
    def _sort_proposals(self, proposals: List[Dict], sort_by: str) -> List[Dict]:
        """Sort proposals based on selected criteria."""
        if sort_by == "Date":
            return sorted(proposals, key=lambda x: x['created'], reverse=True)
        elif sort_by == "Votes":
            return sorted(proposals, key=lambda x: x['votes'], reverse=True)
        elif sort_by == "Protocol":
            return sorted(proposals, key=lambda x: x['protocol'])
        else:
            return proposals
    
    async def _render_proposal_cards(self, proposals: List[Dict]):
        """Render proposal cards with modern styling."""
        for proposal in proposals:
            with st.expander(f"🏛️ {proposal['title']}", expanded=False):
                
                # Create three columns for better layout
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**Protocol:** {proposal['protocol']}")
                    st.markdown(f"**Status:** {self._get_status_badge(proposal['status'])}")
                    st.markdown(f"**Created:** {proposal['created']}")
                    st.markdown(f"**Description:** {proposal['description']}")
                    
                    # Risk factors
                    if proposal.get('risk_factors'):
                        st.markdown("**Risk Factors:**")
                        for factor in proposal['risk_factors']:
                            st.markdown(f"• {factor}")
                
                with col2:
                    # Get volatility data with proper formatting
                    try:
                        vol_data = await get_protocol_volatility(proposal['protocol'].lower())
                        volatility = vol_data.get('volatility')
                        
                        # Import formatting functions
                        from src.models.volatility_model import format_volatility, get_volatility_color
                        
                        formatted_volatility = format_volatility(volatility)
                        vol_color = get_volatility_color(volatility)
                        
                        # Use HTML with title attribute for tooltip
                        volatility_html = f"""
                        <div title="{vol_data.get('data_points', 0)} data points used for forecast">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">Volatility</div>
                            <div style="font-size: 1.2rem; font-weight: 600; color: var(--text-primary);">{vol_color} {formatted_volatility}</div>
                        </div>
                        """
                        st.markdown(volatility_html, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.markdown("""
                        <div title="Unable to fetch volatility data">
                            <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">Volatility</div>
                            <div style="font-size: 1.2rem; font-weight: 600; color: var(--text-primary);">⚪ --</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Sentiment analysis with improved formatting
                    mock_tweets = self._get_mock_tweets(proposal['protocol'])
                    sentiment_score = analyze_sentiment(mock_tweets)
                    sentiment_label = self._get_sentiment_label(sentiment_score)
                    
                    sentiment_html = f"""
                    <div title="Based on {len(mock_tweets)} social media posts">
                        <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">Sentiment</div>
                        <div style="font-size: 1.2rem; font-weight: 600; color: var(--text-primary);">{sentiment_label}</div>
                    </div>
                    """
                    st.markdown(sentiment_html, unsafe_allow_html=True)
                    
                    # Votes with formatting
                    votes_html = f"""
                    <div title="Total governance votes cast">
                        <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">Total Votes</div>
                        <div style="font-size: 1.2rem; font-weight: 600; color: var(--text-primary);">{proposal['votes']:,}</div>
                    </div>
                    """
                    st.markdown(votes_html, unsafe_allow_html=True)
                
                with col3:
                    # Risk assessment
                    try:
                        risk_data = await get_risk_assessment(proposal['protocol'].lower())
                        risk_score = risk_data.get('overall_risk_score', 50)
                        create_risk_indicator(risk_score)
                        
                        # Recommendations
                        recommendations = risk_data.get('recommendations', [])
                        if recommendations:
                            st.markdown("**Recommendations:**")
                            for rec in recommendations[:2]:  # Show first 2
                                st.markdown(f"• {rec}")
                    except:
                        create_risk_indicator(50)  # Default medium risk
                    
                    # Action buttons
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("📊 Details", key=f"details_{proposal['title']}"):
                            st.info("Detailed view coming soon...")
                    with col_btn2:
                        if st.button("🔔 Alert", key=f"alert_{proposal['title']}"):
                            st.success("Alert set successfully!")
                
                st.divider()
    
    def _get_status_badge(self, status: str) -> str:
        """Get styled status badge."""
        status_colors = {
            'active': '🟢',
            'pending': '🟡',
            'executed': '🔵',
            'failed': '🔴'
        }
        return f"{status_colors.get(status.lower(), '⚪')} {status.title()}"
    
    def _get_sentiment_label(self, sentiment_score: float) -> str:
        """Get sentiment label with emoji."""
        if sentiment_score > 0.3:
            return "😊 Positive"
        elif sentiment_score < -0.3:
            return "😠 Negative"
        else:
            return "😐 Neutral"
    
    def _get_mock_tweets(self, protocol: str) -> List[str]:
        """Get mock tweets for sentiment analysis."""
        mock_tweets = {
            'uniswap': [
                "Uniswap V4 looks promising with the new hooks!",
                "Not sure about the complexity of this upgrade.",
                "Great innovation from the Uniswap team!"
            ],
            'aave': [
                "Aave's interest rate model update is needed.",
                "Worried about liquidation risks with this change.",
                "Bullish on AAVE after this proposal!"
            ],
            'compound': [
                "Compound governance migration is risky.",
                "Love the new token structure approach.",
                "COMP holders should vote carefully on this."
            ]
        }
        return mock_tweets.get(protocol.lower(), ["Looks interesting", "Need more info", "Cautiously optimistic"])
    
    def render_timeline_chart(self, proposals: List[Dict]):
        """Render interactive timeline chart."""
        st.subheader("📈 Timeline Visualization")
        
        # Prepare data for timeline
        timeline_data = []
        for proposal in proposals:
            timeline_data.append({
                'Protocol': proposal['protocol'],
                'Title': proposal['title'][:30] + '...' if len(proposal['title']) > 30 else proposal['title'],
                'Status': proposal['status'],
                'Created': proposal['created'],
                'Votes': proposal['votes']
            })
        
        df = pd.DataFrame(timeline_data)
        
        # Create interactive timeline
        fig = px.scatter(
            df,
            x='Created',
            y='Protocol',
            size='Votes',
            color='Status',
            hover_data=['Title', 'Votes'],
            title="Protocol Upgrade Timeline",
            color_discrete_map={
                'active': '#51CF66',
                'pending': '#FFD43B',
                'executed': '#00D4FF',
                'failed': '#FF5252'
            }
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#FAFAFA'),
            xaxis=dict(gridcolor='#2D3748'),
            yaxis=dict(gridcolor='#2D3748'),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Main function to be called from the app
async def render_enhanced_timeline():
    """Render the enhanced timeline interface."""
    timeline = EnhancedTimeline()
    
    # Add tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Proposals", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        await timeline.render_timeline()
    
    with tab2:
        timeline.render_timeline_chart(timeline.mock_proposals)
        
        # Additional analytics
        st.subheader("📊 Analytics Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Proposals", len(timeline.mock_proposals))
        
        with col2:
            active_count = len([p for p in timeline.mock_proposals if p['status'] == 'active'])
            st.metric("Active Proposals", active_count)
        
        with col3:
            total_votes = sum(p['votes'] for p in timeline.mock_proposals)
            st.metric("Total Votes", f"{total_votes:,}")
        
        with col4:
            avg_risk = 65.5  # Mock average risk score
            st.metric("Avg Risk Score", f"{avg_risk:.1f}/100")
    
    with tab3:
        st.subheader("⚙️ Settings")
        
        # Notification settings
        st.checkbox("📧 Email notifications", value=True)
        st.checkbox("📱 Push notifications", value=False)
        st.checkbox("🔔 Risk alerts", value=True)
        
        # Filter preferences
        st.selectbox("Default status filter", ["All", "Active", "Pending"])
        st.selectbox("Default sort order", ["Date", "Risk Score", "Votes"])
        
        # Risk thresholds
        st.slider("Risk alert threshold", 0, 100, 75)
        st.slider("Volatility alert threshold", 0, 100, 60)

if __name__ == "__main__":
    asyncio.run(render_enhanced_timeline())
