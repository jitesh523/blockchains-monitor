"""
Tests for src.ui.theme
Migrated from legacy test_theme_audit.py to Pytest.
"""

import math
import sys
from unittest.mock import MagicMock

if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = MagicMock()

from src.ui.theme import (
    calculate_contrast_ratio,
    get_theme_audit_results,
    get_theme_colors
)


def test_calculate_contrast_ratio():
    """Test WCAG contrast ratio math."""
    ratio = calculate_contrast_ratio("#000000", "#FFFFFF")
    assert math.isclose(ratio, 21.0, rel_tol=1e-2)
    
    ratio_same = calculate_contrast_ratio("#123456", "#123456")
    assert math.isclose(ratio_same, 1.0, rel_tol=1e-2)


def test_get_theme_colors():
    """Verify theme dictionaries have expected keys."""
    dark = get_theme_colors(dark_mode=True)
    light = get_theme_colors(dark_mode=False)
    
    expected_keys = {"background", "text_primary", "text_secondary", "primary", "secondary", "error", "warning"}
    
    for key in expected_keys:
        assert key in dark
        assert key in light
        
    assert dark["background"] != light["background"]


def test_theme_audit_results():
    """Verify that the theme audit tool actually executes contrast checks."""
    dark_audit = get_theme_audit_results(dark_mode=True)
    
    assert "theme_mode" in dark_audit
    assert "passed" in dark_audit
    assert "failed" in dark_audit
    assert "warnings" in dark_audit
    
    # Text vs Background should pass in standard themes
    passed_texts = " ".join(dark_audit["passed"]).lower()
    assert "text on background" in passed_texts
