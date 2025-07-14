import streamlit as st
from typing import Dict, Any

# Color palette for dark theme
DARK_THEME = {
    'primary': '#00D4FF',
    'secondary': '#FF6B6B',
    'success': '#51CF66',
    'warning': '#FFD43B',
    'error': '#FF5252',
    'background': '#0E1117',
    'surface': '#1E2329',
    'card': '#262D3A',
    'text_primary': '#FAFAFA',
    'text_secondary': '#B0B3B8',
    'border': '#2D3748',
    'hover': '#2A3441'
}

# Color palette for light theme
LIGHT_THEME = {
    'primary': '#0066CC',
    'secondary': '#FF4444',
    'success': '#28A745',
    'warning': '#FFC107',
    'error': '#DC3545',
    'background': '#FFFFFF',
    'surface': '#F8F9FA',
    'card': '#FFFFFF',
    'text_primary': '#212529',
    'text_secondary': '#6C757D',
    'border': '#E9ECEF',
    'hover': '#F8F9FA'
}

def get_theme_colors(dark_mode: bool = True) -> Dict[str, str]:
    """Get theme colors based on mode."""
    return DARK_THEME if dark_mode else LIGHT_THEME

def inject_custom_css(dark_mode: bool = True):
    """Inject custom CSS for modern UI styling."""
    theme = get_theme_colors(dark_mode)
    
    css = f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables */
    :root {{
        --primary-color: {theme['primary']};
        --secondary-color: {theme['secondary']};
        --success-color: {theme['success']};
        --warning-color: {theme['warning']};
        --error-color: {theme['error']};
        --background-color: {theme['background']};
        --surface-color: {theme['surface']};
        --card-color: {theme['card']};
        --text-primary: {theme['text_primary']};
        --text-secondary: {theme['text_secondary']};
        --border-color: {theme['border']};
        --hover-color: {theme['hover']};
    }}
    
    /* Global styles */
    .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: var(--background-color);
        color: var(--text-primary);
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Animated title */
    .main-title {{
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 2rem;
        animation: titleFadeIn 1s ease-out;
    }}
    
    @keyframes titleFadeIn {{
        from {{
            opacity: 0;
            transform: translateY(-30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    /* Proposal cards */
    .proposal-card {{
        background: var(--card-color);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    
    .proposal-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 24px rgba(0, 212, 255, 0.15);
        border-color: var(--primary-color);
    }}
    
    .proposal-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }}
    
    .proposal-card:hover::before {{
        transform: scaleX(1);
    }}
    
    .proposal-title {{
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }}
    
    .proposal-meta {{
        color: var(--text-secondary);
        font-size: 0.875rem;
        margin-bottom: 1rem;
    }}
    
    .proposal-status {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }}
    
    .status-active {{
        background: rgba(81, 207, 102, 0.2);
        color: var(--success-color);
    }}
    
    .status-pending {{
        background: rgba(255, 212, 59, 0.2);
        color: var(--warning-color);
    }}
    
    .status-failed {{
        background: rgba(255, 82, 82, 0.2);
        color: var(--error-color);
    }}
    
    /* Metrics grid */
    .metrics-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }}
    
    .metric-card {{
        background: var(--surface-color);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s ease;
    }}
    
    .metric-card:hover {{
        background: var(--hover-color);
        transform: translateY(-2px);
    }}
    
    .metric-value {{
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
    }}
    
    .metric-label {{
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background: var(--surface-color);
        border-right: 1px solid var(--border-color);
    }}
    
    .css-1d391kg .css-1v0mbdj {{
        background: var(--surface-color);
    }}
    
    /* Network status cards */
    .network-status {{
        background: var(--card-color);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }}
    
    .network-status:hover {{
        border-color: var(--primary-color);
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.1);
    }}
    
    .network-name {{
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }}
    
    .network-metric {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 0.25rem 0;
    }}
    
    .network-metric-label {{
        color: var(--text-secondary);
        font-size: 0.875rem;
    }}
    
    .network-metric-value {{
        color: var(--text-primary);
        font-weight: 500;
    }}
    
    /* Button styling */
    .stButton > button {{
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 212, 255, 0.4);
    }}
    
    /* Selectbox styling */
    .stSelectbox > div > div {{
        background: var(--card-color);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        transition: all 0.3s ease;
    }}
    
    .stSelectbox > div > div:hover {{
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
    }}
    
    /* Metric styling */
    .stMetric {{
        background: var(--card-color);
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }}
    
    .stMetric:hover {{
        border-color: var(--primary-color);
        transform: translateY(-2px);
    }}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--surface-color);
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--border-color);
        border-radius: 4px;
        transition: background 0.3s ease;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--primary-color);
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background: var(--card-color);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        transition: all 0.3s ease;
    }}
    
    .streamlit-expanderHeader:hover {{
        border-color: var(--primary-color);
        box-shadow: 0 2px 8px rgba(0, 212, 255, 0.1);
    }}
    
    /* Loading animation */
    .loading-spinner {{
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid var(--border-color);
        border-radius: 50%;
        border-top-color: var(--primary-color);
        animation: spin 1s ease-in-out infinite;
    }}
    
    @keyframes spin {{
        to {{ transform: rotate(360deg); }}
    }}
    
    /* Risk indicator */
    .risk-indicator {{
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
    }}
    
    .risk-low {{
        background: rgba(81, 207, 102, 0.2);
        color: var(--success-color);
    }}
    
    .risk-medium {{
        background: rgba(255, 212, 59, 0.2);
        color: var(--warning-color);
    }}
    
    .risk-high {{
        background: rgba(255, 82, 82, 0.2);
        color: var(--error-color);
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .main-title {{
            font-size: 2rem;
        }}
        
        .proposal-card {{
            padding: 1rem;
        }}
        
        .metrics-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    
    /* Theme toggle */
    .theme-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: var(--card-color);
        border: 1px solid var(--border-color);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
    }}
    
    .theme-toggle:hover {{
        border-color: var(--primary-color);
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.2);
    }}
    
    /* Animation utilities */
    .fade-in {{
        animation: fadeIn 0.5s ease-out;
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .slide-in-right {{
        animation: slideInRight 0.5s ease-out;
    }}
    
    @keyframes slideInRight {{
        from {{ opacity: 0; transform: translateX(50px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    .slide-in-left {{
        animation: slideInLeft 0.5s ease-out;
    }}
    
    @keyframes slideInLeft {{
        from {{ opacity: 0; transform: translateX(-50px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def create_animated_title(title: str, subtitle: str = None):
    """Create an animated title with gradient effect."""
    html = f"""
    <div class="main-title">{title}</div>
    """
    if subtitle:
        html += f"""
        <div style="text-align: center; color: var(--text-secondary); margin-top: -1rem; margin-bottom: 2rem;">
            {subtitle}
        </div>
        """
    
    st.markdown(html, unsafe_allow_html=True)

def create_proposal_card(proposal: Dict[str, Any], metrics: Dict[str, Any]):
    """Create a modern proposal card with hover effects."""
    status_class = f"status-{proposal.get('status', 'pending').lower()}"
    
    html = f"""
    <div class="proposal-card fade-in">
        <div class="proposal-title">{proposal.get('title', 'Untitled Proposal')}</div>
        <div class="proposal-meta">
            📅 {proposal.get('created', 'Unknown')} • ⛓️ {proposal.get('protocol', 'Unknown')}
        </div>
        <div class="proposal-status {status_class}">
            {proposal.get('status', 'pending')}
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{metrics.get('volatility', 'N/A')}</div>
                <div class="metric-label">Volatility</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('sentiment', 'N/A')}</div>
                <div class="metric-label">Sentiment</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{metrics.get('risk_score', 'N/A')}</div>
                <div class="metric-label">Risk Score</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def create_network_status_card(network: str, metrics: Dict[str, Any]):
    """Create a network status card."""
    html = f"""
    <div class="network-status slide-in-left">
        <div class="network-name">🔗 {network.title()}</div>
        <div class="network-metric">
            <span class="network-metric-label">Gas Price</span>
            <span class="network-metric-value">{metrics.get('gas_price', 'N/A')}</span>
        </div>
        <div class="network-metric">
            <span class="network-metric-label">Block Time</span>
            <span class="network-metric-value">{metrics.get('block_time', 'N/A')}</span>
        </div>
        <div class="network-metric">
            <span class="network-metric-label">TPS</span>
            <span class="network-metric-value">{metrics.get('tps', 'N/A')}</span>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def create_risk_indicator(risk_score: float):
    """Create a risk indicator with color coding."""
    if risk_score <= 30:
        risk_class = "risk-low"
        risk_text = "🟢 Low Risk"
    elif risk_score <= 60:
        risk_class = "risk-medium"
        risk_text = "🟡 Medium Risk"
    else:
        risk_class = "risk-high"
        risk_text = "🔴 High Risk"
    
    html = f"""
    <div class="risk-indicator {risk_class}">
        {risk_text} ({risk_score:.1f}/100)
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def create_loading_spinner():
    """Create a loading spinner."""
    html = """
    <div style="display: flex; justify-content: center; align-items: center; padding: 2rem;">
        <div class="loading-spinner"></div>
        <span style="margin-left: 1rem; color: var(--text-secondary);">Loading...</span>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def create_theme_toggle():
    """Create a theme toggle button."""
    html = """
    <div class="theme-toggle" onclick="toggleTheme()">
        <span id="theme-icon">🌙</span>
    </div>
    
    <script>
    function toggleTheme() {
        const icon = document.getElementById('theme-icon');
        if (icon.innerHTML === '🌙') {
            icon.innerHTML = '☀️';
            // Add light theme toggle logic here
        } else {
            icon.innerHTML = '🌙';
            // Add dark theme toggle logic here
        }
    }
    </script>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def apply_theme(dark_mode: bool = True):
    """Apply the theme to the entire application."""
    inject_custom_css(dark_mode)
    
    # Store theme preference in session state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = dark_mode
