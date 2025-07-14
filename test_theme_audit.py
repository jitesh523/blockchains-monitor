#!/usr/bin/env python3
"""
Test script to verify theme audit functionality and contrast checking.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ui.theme import get_theme_audit_results, get_theme_colors

def test_theme_audit():
    """Test the theme audit functionality for both light and dark modes."""
    print("🎨 Testing Theme Audit Functionality")
    print("=" * 50)
    
    # Test dark mode
    print("\n🌙 DARK MODE AUDIT")
    print("-" * 30)
    dark_audit = get_theme_audit_results(dark_mode=True)
    print(f"Theme: {dark_audit['theme_mode']}")
    
    print("\n✅ PASSED:")
    for passed_item in dark_audit['passed']:
        print(f"  • {passed_item}")
    
    print("\n❌ FAILED:")
    for failed_item in dark_audit['failed']:
        print(f"  • {failed_item}")
    
    print("\n⚠️  WARNINGS:")
    for warning_item in dark_audit['warnings']:
        print(f"  • {warning_item}")
    
    # Test light mode
    print("\n\n☀️  LIGHT MODE AUDIT")
    print("-" * 30)
    light_audit = get_theme_audit_results(dark_mode=False)
    print(f"Theme: {light_audit['theme_mode']}")
    
    print("\n✅ PASSED:")
    for passed_item in light_audit['passed']:
        print(f"  • {passed_item}")
    
    print("\n❌ FAILED:")
    for failed_item in light_audit['failed']:
        print(f"  • {failed_item}")
    
    print("\n⚠️  WARNINGS:")
    for warning_item in light_audit['warnings']:
        print(f"  • {warning_item}")
    
    # Summary
    print("\n\n📊 SUMMARY")
    print("-" * 30)
    print(f"Dark Mode - Passed: {len(dark_audit['passed'])}, Failed: {len(dark_audit['failed'])}, Warnings: {len(dark_audit['warnings'])}")
    print(f"Light Mode - Passed: {len(light_audit['passed'])}, Failed: {len(light_audit['failed'])}, Warnings: {len(light_audit['warnings'])}")
    
    # Show theme colors for reference
    print("\n\n🎨 THEME COLORS")
    print("-" * 30)
    dark_colors = get_theme_colors(dark_mode=True)
    light_colors = get_theme_colors(dark_mode=False)
    
    print("\nDark Theme Colors:")
    for key, value in dark_colors.items():
        print(f"  {key}: {value}")
    
    print("\nLight Theme Colors:")
    for key, value in light_colors.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_theme_audit()
