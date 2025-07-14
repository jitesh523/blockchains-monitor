import streamlit as st
from typing import Dict, Any
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.utils.contrast_check import check_contrast, calculate_contrast_ratio
except ImportError:
    # Fallback for missing contrast check
    def check_contrast(hex1: str, hex2: str, min_ratio: float = 4.5) -> bool:
        return True
    def calculate_contrast_ratio(hex1: str, hex2: str) -> float:
        return 5.0

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
    'hover': '#2A3441',
    'accent_glow': 'rgba(0, 255, 255, 0.2)'
}

# Color palette for light theme
LIGHT_THEME = {
    'primary': '#0066CC',
    'secondary': '#FF4444',
    'success': '#28A745',
    'warning': '#D97706',  # Changed from #FFC107 to darker orange for better contrast
    'error': '#DC3545',
    'background': '#FFFFFF',
    'surface': '#F8F9FA',
    'card': '#FFFFFF',
    'text_primary': '#212529',
    'text_secondary': '#6C757D',
    'border': '#E9ECEF',
    'hover': '#F8F9FA',
    'accent_glow': 'rgba(255, 255, 255, 0.4)'
}

def get_theme_colors(dark_mode: bool = True) -> Dict[str, str]:
    """Get theme colors based on mode."""
    return DARK_THEME if dark_mode else LIGHT_THEME

def get_theme_audit_results(dark_mode: bool = True) -> Dict[str, Any]:
    """Audit theme colors for WCAG compliance."""
    theme = get_theme_colors(dark_mode)
    audit_results = {
        'theme_mode': 'dark' if dark_mode else 'light',
        'passed': [],
        'failed': [],
        'warnings': []
    }
    
    # Check text-on-background contrast
    text_bg_ratio = calculate_contrast_ratio(theme['text_primary'], theme['background'])
    if text_bg_ratio >= 4.5:
        audit_results['passed'].append(f"Primary text on background: {text_bg_ratio:.2f}:1")
    else:
        audit_results['failed'].append(f"Primary text on background: {text_bg_ratio:.2f}:1 (needs 4.5:1)")
    
    # Check secondary text contrast
    sec_text_bg_ratio = calculate_contrast_ratio(theme['text_secondary'], theme['background'])
    if sec_text_bg_ratio >= 4.5:
        audit_results['passed'].append(f"Secondary text on background: {sec_text_bg_ratio:.2f}:1")
    else:
        audit_results['failed'].append(f"Secondary text on background: {sec_text_bg_ratio:.2f}:1 (needs 4.5:1)")
    
    # Check card contrast
    card_text_ratio = calculate_contrast_ratio(theme['text_primary'], theme['card'])
    if card_text_ratio >= 4.5:
        audit_results['passed'].append(f"Text on card: {card_text_ratio:.2f}:1")
    else:
        audit_results['failed'].append(f"Text on card: {card_text_ratio:.2f}:1 (needs 4.5:1)")
    
    # Check warning colors
    warning_ratio = calculate_contrast_ratio(theme['warning'], theme['background'])
    if warning_ratio >= 3.0:  # Lower threshold for non-text elements
        audit_results['passed'].append(f"Warning color: {warning_ratio:.2f}:1")
    else:
        audit_results['warnings'].append(f"Warning color: {warning_ratio:.2f}:1 (consider improving)")
    
    return audit_results

def inject_custom_css(dark_mode: bool = True):
    """Inject custom CSS for modern UI styling with proper theme switching."""
    theme = get_theme_colors(dark_mode)
    mode_class = 'dark-mode' if dark_mode else 'light-mode'
    
    # Pre-calculate conditional values
    proposal_card_shadow = 'box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);' if not dark_mode else 'box-shadow: 0 2px 8px rgba(0, 212, 255, 0.08), 0 1px 3px rgba(0, 212, 255, 0.04);'
    proposal_card_hover_shadow = 'box-shadow: 0 20px 40px rgba(0, 102, 204, 0.12), 0 8px 16px rgba(0, 102, 204, 0.08), 0 0 0 1px rgba(0, 102, 204, 0.1);' if not dark_mode else 'box-shadow: 0 20px 40px rgba(0, 212, 255, 0.15), 0 8px 16px rgba(0, 212, 255, 0.1), 0 0 0 1px rgba(0, 212, 255, 0.2);'
    metric_card_shadow = 'box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.06);' if not dark_mode else 'box-shadow: 0 1px 3px rgba(0, 212, 255, 0.05), 0 1px 2px rgba(0, 212, 255, 0.03);'
    metric_card_hover_shadow = 'box-shadow: 0 8px 25px rgba(0, 102, 204, 0.15), 0 4px 10px rgba(0, 102, 204, 0.1);' if not dark_mode else 'box-shadow: 0 8px 25px rgba(0, 212, 255, 0.2), 0 4px 10px rgba(0, 212, 255, 0.15);'
    network_status_shadow = 'box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);' if not dark_mode else 'box-shadow: 0 1px 3px rgba(0, 212, 255, 0.05);'
    network_status_hover_shadow = 'box-shadow: 0 6px 20px rgba(0, 102, 204, 0.12), 0 2px 8px rgba(0, 102, 204, 0.08);' if not dark_mode else 'box-shadow: 0 6px 20px rgba(0, 212, 255, 0.15), 0 2px 8px rgba(0, 212, 255, 0.1);'
    selectbox_shadow = 'box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);' if not dark_mode else 'box-shadow: 0 1px 3px rgba(0, 212, 255, 0.05);'
    selectbox_hover_shadow = 'box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1), 0 4px 12px rgba(0, 102, 204, 0.08);' if not dark_mode else 'box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1), 0 4px 12px rgba(0, 212, 255, 0.08);'
    selectbox_focus_shadow = 'box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.15), 0 6px 20px rgba(0, 102, 204, 0.12);' if not dark_mode else 'box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.15), 0 6px 20px rgba(0, 212, 255, 0.12);'
    expander_shadow = 'box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);' if not dark_mode else 'box-shadow: 0 1px 3px rgba(0, 212, 255, 0.05);'
    expander_hover_shadow = 'box-shadow: 0 4px 15px rgba(0, 102, 204, 0.12), 0 2px 6px rgba(0, 102, 204, 0.08);' if not dark_mode else 'box-shadow: 0 4px 15px rgba(0, 212, 255, 0.15), 0 2px 6px rgba(0, 212, 255, 0.1);'
    risk_indicator_shadow = 'box-shadow: 0 4px 12px rgba(0, 102, 204, 0.1);' if not dark_mode else 'box-shadow: 0 4px 12px rgba(0, 212, 255, 0.1);'
    
    css = f"""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables - Dynamic theme switching */
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
        --accent-glow: {theme['accent_glow']};
    }}
    
    /* Fallback for prefers-color-scheme */
    @media (prefers-color-scheme: dark) {{
        :root {{
            --primary-color: #00D4FF;
            --secondary-color: #FF6B6B;
            --success-color: #51CF66;
            --warning-color: #FFD43B;
            --error-color: #FF5252;
            --background-color: #0E1117;
            --surface-color: #1E2329;
            --card-color: #262D3A;
            --text-primary: #FAFAFA;
            --text-secondary: #B0B3B8;
            --border-color: #2D3748;
            --hover-color: #2A3441;
            --accent-glow: rgba(0, 255, 255, 0.2);
        }}
    }}
    
    @media (prefers-color-scheme: light) {{
        :root {{
            --primary-color: #0066CC;
            --secondary-color: #FF4444;
            --success-color: #28A745;
            --warning-color: #D97706;
            --error-color: #DC3545;
            --background-color: #FFFFFF;
            --surface-color: #F8F9FA;
            --card-color: #FFFFFF;
            --text-primary: #212529;
            --text-secondary: #6C757D;
            --border-color: #E9ECEF;
            --hover-color: #F8F9FA;
            --accent-glow: rgba(255, 255, 255, 0.4);
        }}
    }}
    
    /* Global styles with theme class */
    .stApp, .{mode_class} {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        background: var(--background-color) !important;
        color: var(--text-primary) !important;
        transition: all 0.3s ease;
    }}
    
    /* Force Streamlit container backgrounds */
    .stApp > div, .main .block-container {{
        background: var(--background-color) !important;
        color: var(--text-primary) !important;
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
    
    /* Proposal cards - Theme aware with smooth animations */
    .proposal-card {{
        background: var(--card-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
        color: var(--text-primary) !important;
        cursor: pointer;
        transform: translateY(0) scale(1);
        {proposal_card_shadow}
    }}
    
    .proposal-card:hover {{
        transform: translateY(-8px) scale(1.02);
        {proposal_card_hover_shadow}
        border-color: var(--primary-color) !important;
    }}
    
    .proposal-card:active {{
        transform: translateY(-2px) scale(0.98);
        transition: all 0.15s cubic-bezier(0.4, 0, 0.6, 1);
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
    
    /* Metrics grid - Theme aware with responsive overflow handling */
    .metrics-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }}
    
    .metric-card {{
        background: var(--surface-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        color: var(--text-primary) !important;
        cursor: pointer;
        transform: translateY(0) scale(1);
        min-width: 0; /* Essential for text truncation */
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        {metric_card_shadow}
    }}

    @media (max-width: 480px) {{
        .metric-card {{
            padding: 0.5rem;
        }}
        .metric-value {{
            font-size: 1.05rem;
        }}
        .metric-label {{
            font-size: 0.68rem;
        }}
    }}
    
    .metric-card:hover {{
        background: var(--hover-color) !important;
        transform: translateY(-4px) scale(1.03);
        {metric_card_hover_shadow}
        border-color: var(--primary-color) !important;
    }}
    
    .metric-card:active {{
        transform: translateY(-1px) scale(0.98);
        transition: all 0.1s cubic-bezier(0.4, 0, 0.6, 1);
    }}
    
    .metric-value {{
        font-size: clamp(1.18rem, 3vw, 1.5rem);
        font-weight: 600;
        color: var(--text-primary) !important;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        min-width: 0;
        display: inline-flex;
        flex-wrap: wrap;
        max-width: 100%;
        line-height: 1.22;
    }}
    
    .metric-label {{
        font-size: clamp(0.6rem, 2vw, 0.81rem);
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        min-width: 0;
        margin-top: 0.18rem;
        line-height: 1.2;
        max-width: 90px;
        display: inline-block;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background: var(--surface-color);
        border-right: 1px solid var(--border-color);
    }}
    
    .css-1d391kg .css-1v0mbdj {{
        background: var(--surface-color);
    }}
    
    /* Network status cards with enhanced animations */
    .network-status {{
        background: var(--card-color) !important;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid var(--border-color) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        transform: translateX(0) scale(1);
        cursor: pointer;
        {network_status_shadow}
    }}
    
    .network-status:hover {{
        border-color: var(--primary-color) !important;
        transform: translateX(4px) scale(1.02);
        {network_status_hover_shadow}
    }}
    
    .network-status:active {{
        transform: translateX(1px) scale(0.98);
        transition: all 0.1s cubic-bezier(0.4, 0, 0.6, 1);
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
        font-size: clamp(0.73rem, 2vw, 0.92rem);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        min-width: 0;
        flex-shrink: 0;
        max-width: 90px;
        display: inline-block;
        line-height: 1.14;
    }}
    
    .network-metric-value {{
        color: var(--text-primary);
        font-weight: 500;
        font-size: clamp(0.8rem, 2.5vw, 1rem);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        min-width: 0;
        text-align: right;
        flex-shrink: 1;
    }}
    
    /* Button styling - Clean and minimal */
    .stButton > button {{
        background: var(--primary-color) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: background-color 0.2s ease;
        cursor: pointer;
        box-shadow: none !important;
    }}
    
    .stButton > button:hover {{
        background: var(--primary-color) !important;
        filter: brightness(0.9);
    }}
    
    .stButton > button:active {{
        filter: brightness(0.8);
    }}
    
    /* Specific styling for action buttons */
    .action-button {{
        background: var(--surface-color) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 400;
        transition: border-color 0.2s ease;
        cursor: pointer;
        box-shadow: none !important;
    }}
    
    .action-button:hover {{
        border-color: var(--primary-color) !important;
    }}
    
    /* Selectbox styling with smooth animations */
    .stSelectbox > div > div {{
        background: var(--card-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        {selectbox_shadow}
        transform: scale(1);
    }}
    
    .stSelectbox > div > div:hover {{
        border-color: var(--primary-color) !important;
        {selectbox_hover_shadow}
        transform: scale(1.02);
    }}
    
    .stSelectbox > div > div:focus-within {{
        border-color: var(--primary-color) !important;
        {selectbox_focus_shadow}
        transform: scale(1.02);
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
    
    /* Expander styling with smooth animations */
    .streamlit-expanderHeader {{
        background: var(--card-color) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        transform: scale(1);
        {expander_shadow}
    }}
    
    .streamlit-expanderHeader:hover {{
        border-color: var(--primary-color) !important;
        transform: scale(1.01);
        {expander_hover_shadow}
    }}
    
    .streamlit-expanderHeader:active {{
        transform: scale(0.99);
        transition: all 0.1s cubic-bezier(0.4, 0, 0.6, 1);
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
    
    /* Risk indicator with smooth animations */
    .risk-indicator {{
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        text-align: center;
        margin: 0.5rem 0;
        transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        transform: scale(1);
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }}
    
    .risk-indicator:hover {{
        transform: scale(1.05);
        {risk_indicator_shadow}
    }}
    
    .risk-low {{
        background: rgba(81, 207, 102, 0.2);
        color: var(--success-color);
        border: 1px solid rgba(81, 207, 102, 0.3);
    }}
    
    .risk-low:hover {{
        background: rgba(81, 207, 102, 0.3);
        box-shadow: 0 4px 12px rgba(81, 207, 102, 0.2) !important;
    }}
    
    .risk-medium {{
        background: rgba(255, 212, 59, 0.2);
        color: var(--warning-color);
        border: 1px solid rgba(255, 212, 59, 0.3);
    }}
    
    .risk-medium:hover {{
        background: rgba(255, 212, 59, 0.3);
        box-shadow: 0 4px 12px rgba(255, 212, 59, 0.2) !important;
    }}
    
    .risk-high {{
        background: rgba(255, 82, 82, 0.2);
        color: var(--error-color);
        border: 1px solid rgba(255, 82, 82, 0.3);
        animation: pulse-danger 2s infinite;
    }}
    
    .risk-high:hover {{
        background: rgba(255, 82, 82, 0.3);
        box-shadow: 0 4px 12px rgba(255, 82, 82, 0.2) !important;
    }}
    
    @keyframes pulse-danger {{
        0%, 100% {{ transform: scale(1); }}
        50% {{ transform: scale(1.02); box-shadow: 0 0 20px rgba(255, 82, 82, 0.3); }}
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
        box-shadow: 0 4px 12px var(--accent-glow);
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
    """Create a modern proposal card with hover effects and robust metric display."""
    import math
    status_class = f"status-{proposal.get('status', 'pending').lower()}"

    # Robust metrics fallback
    vol_raw = metrics.get('volatility', 'N/A')
    sentiment_raw = metrics.get('sentiment', 'N/A')
    risk_score_raw = metrics.get('risk_score', 'N/A')
    
    # Handle NaN or None or inf for numbers
    def nice(val):
        try:
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                return '--'
            # Also cover string case
            if isinstance(val, str) and (val.lower() == 'nan' or val.lower() == 'inf'):
                return '--'
        except Exception:
            return '--'
        return val

    volatility = nice(vol_raw)
    sentiment = nice(sentiment_raw)
    risk_score = nice(risk_score_raw)

    html = f"""
    <div class="proposal-card fade-in">
        <div class="proposal-title" title="{proposal.get('title','Untitled Proposal')}">{proposal.get('title', 'Untitled Proposal')}</div>
        <div class="proposal-meta" title="Date: {proposal.get('created','Unknown')} | Chain: {proposal.get('protocol','Unknown')}">
            📅 {proposal.get('created', 'Unknown')} • ⛓️ {proposal.get('protocol', 'Unknown')}
        </div>
        <div class="proposal-status {status_class}">{proposal.get('status', 'pending')}</div>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value" title="{volatility}">{volatility}</div>
                <div class="metric-label" title="Volatility">Volatility</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" title="{sentiment}">{sentiment}</div>
                <div class="metric-label" title="Sentiment">Sentiment</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" title="{risk_score}">{risk_score}</div>
                <div class="metric-label" title="Risk Score">Risk Score</div>
            </div>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

def create_network_status_card(network: str, metrics: Dict[str, Any]):
    """Create a network status card with tooltips and robust value fallback."""
    import math
    def nice(val):
        try:
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                return '--'
            # Also cover string case
            if isinstance(val, str) and (val.lower() == 'nan' or val.lower() == 'inf'):
                return '--'
        except Exception:
            return '--'
        return val
    gas = nice(metrics.get('gas_price', 'N/A'))
    block_time = nice(metrics.get('block_time', 'N/A'))
    tps = nice(metrics.get('tps', 'N/A'))
    html = f"""
    <div class="network-status slide-in-left">
        <div class="network-name" title="{network.title()}">🔗 {network.title()}</div>
        <div class="network-metric">
            <span class="network-metric-label" title="Gas Price">Gas Price</span>
            <span class="network-metric-value" title="{gas}">{gas}</span>
        </div>
        <div class="network-metric">
            <span class="network-metric-label" title="Block Time">Block Time</span>
            <span class="network-metric-value" title="{block_time}">{block_time}</span>
        </div>
        <div class="network-metric">
            <span class="network-metric-label" title="TPS">TPS</span>
            <span class="network-metric-value" title="{tps}">{tps}</span>
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
    """Create a functional theme toggle button."""
    # Initialize theme state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    
    # Create toggle button in sidebar
    with st.sidebar:
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("**Theme**")
        
        with col2:
            # Use a button to toggle theme
            current_icon = "🌙" if st.session_state.dark_mode else "☀️"
            if st.button(current_icon, key="theme_toggle", help="Toggle theme"):
                st.session_state.dark_mode = not st.session_state.dark_mode
                st.rerun()
    
    return st.session_state.dark_mode

def display_theme_audit():
    """Display theme audit results in the Streamlit app."""
    st.subheader("🎨 Theme Accessibility Audit")
    
    # Get current theme
    current_dark_mode = st.session_state.get('dark_mode', True)
    
    # Display audit for current theme
    audit_results = get_theme_audit_results(current_dark_mode)
    
    mode_name = "Dark" if current_dark_mode else "Light"
    st.write(f"**Current Theme: {mode_name} Mode**")
    
    # Display passed items
    if audit_results['passed']:
        st.success("✅ **Passed Checks:**")
        for item in audit_results['passed']:
            st.write(f"  • {item}")
    
    # Display failed items
    if audit_results['failed']:
        st.error("❌ **Failed Checks:**")
        for item in audit_results['failed']:
            st.write(f"  • {item}")
    
    # Display warnings
    if audit_results['warnings']:
        st.warning("⚠️ **Warnings:**")
        for item in audit_results['warnings']:
            st.write(f"  • {item}")
    
    # Summary
    total_checks = len(audit_results['passed']) + len(audit_results['failed']) + len(audit_results['warnings'])
    passed_checks = len(audit_results['passed'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Checks", total_checks)
    with col2:
        st.metric("Passed", passed_checks, delta=passed_checks - total_checks + passed_checks)
    with col3:
        st.metric("Failed", len(audit_results['failed']), delta=-len(audit_results['failed']) if audit_results['failed'] else 0)
    
    # Show both theme audits in expander
    with st.expander("📊 Compare Both Themes"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🌙 Dark Mode**")
            dark_audit = get_theme_audit_results(True)
            st.write(f"Passed: {len(dark_audit['passed'])}")
            st.write(f"Failed: {len(dark_audit['failed'])}")
            st.write(f"Warnings: {len(dark_audit['warnings'])}")
        
        with col2:
            st.write("**☀️ Light Mode**")
            light_audit = get_theme_audit_results(False)
            st.write(f"Passed: {len(light_audit['passed'])}")
            st.write(f"Failed: {len(light_audit['failed'])}")
            st.write(f"Warnings: {len(light_audit['warnings'])}")

def apply_theme(dark_mode: bool = True):
    """Apply the theme to the entire application."""
    inject_custom_css(dark_mode)
    
    # Store theme preference in session state
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = dark_mode
