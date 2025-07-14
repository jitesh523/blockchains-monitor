import streamlit as st

def suggest_execution(risk_score: float) -> str:
    """Provide execution guidance based on risk score."""
    if risk_score > 75:
        return "⚠️ High risk detected. Exit volatile assets. Consider stablecoins or short hedge."
    elif risk_score > 50:
        return "🟡 Medium risk. Monitor closely. Reduce exposure by 20%."
    else:
        return "🟢 Low risk. No action needed. Opportunity to enter long positions."

def render_execution_guidance(risk_score: float):
    """Render execution guidance in the Streamlit UI based on risk score."""
    from src.ui.theme import create_risk_indicator
    
    st.subheader("🎯 Execution Guidance")
    
    # Risk indicator
    create_risk_indicator(risk_score)
    
    # Main guidance
    guidance = suggest_execution(risk_score)
    
    if risk_score > 80:
        st.error("🚨 HIGH RISK: Exit volatile tokens. Move to stables or hedge.")
    elif risk_score > 50:
        st.warning("⚠️ MODERATE RISK: Watch closely. Reduce exposure 10–30%.")
    else:
        st.success("✅ LOW RISK: Favorable for long positions. Monitor sentiment shifts.")
    
    st.caption("Recommendations auto-adjust based on market data.")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Portfolio", use_container_width=True):
            st.info("Portfolio analysis coming soon...")
    
    with col2:
        if st.button("🔔 Set Alert", use_container_width=True):
            st.success("Alert configured!")
    
    # Quick stats
    st.markdown("#### 📊 Quick Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Risk Level", f"{risk_score:.1f}/100")
    
    with col2:
        volatility = 45.2  # Mock volatility
        st.metric("Volatility", f"{volatility:.1f}%")
    
    # Recent activity
    st.markdown("#### 🕰️ Recent Activity")
    
    activities = [
        "🟢 Uniswap proposal approved",
        "🟡 Aave governance vote started",
        "🔴 Compound risk alert triggered"
    ]
    
    for activity in activities:
        st.markdown(f"• {activity}")

    # Bundle the Proposal Card UI
    def display_proposal_card(proposal, volatility, sentiment_label, sentiment, risk_score):
        with st.container():
            st.markdown(f"### 🧾 {proposal['title']}")
            st.write(f"📅 {proposal['created_date'].strftime('%b %d, %Y')} • ⛓️ {proposal.get('network', 'Unknown')}")
            st.markdown(f"**Status:** {proposal['status']}")
            st.metric("Volatility (ann.)", f"{volatility} %")
            st.metric("Sentiment", sentiment_label, delta=f"{sentiment}")
            st.metric("Risk Score", f"{risk_score}/100")
            st.divider()

    return display_proposal_card

# Example usage
if __name__ == "__main__":
    st.title("Execution Guidance Example")
    example_risk_score = 68.5
    
    # Mock proposal details
    example_proposal = {
        'title': 'Improve Liquidity Efficiency',
        'created_date': "2025-07-14T10:00:00",  # Mock date
        'status': 'Active',
        'network': 'Ethereum'
    }

    render_execution_guidance(example_risk_score)

    display_proposal_card = render_execution_guidance(example_risk_score)
    display_proposal_card(
        example_proposal,
        volatility=24.2,
        sentiment_label="😊 Positive",
        sentiment=0.58,
        risk_score=example_risk_score
    )

