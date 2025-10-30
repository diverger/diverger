#!/usr/bin/env python3
"""
Test GitHub Holiday Color Detection

A simple test script to visualize detected colors.
"""

import sys
import json
from detect_github_holiday_colors import (
    fetch_github_profile,
    extract_contribution_colors,
    detect_holiday_theme,
    generate_color_scheme
)


def print_color_box(color, label=""):
    """Print a colored box in terminal (requires ANSI support)."""
    # Convert hex to RGB
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    
    # ANSI escape code for RGB color
    color_code = f"\033[48;2;{r};{g};{b}m"
    reset_code = "\033[0m"
    
    # Print colored box
    text = f" {color} {label} " if label else f" {color} "
    print(f"{color_code}{text}{reset_code}", end=" ")


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "diverger"
    
    print(f"\n🔍 Testing GitHub Holiday Color Detection for: {username}\n")
    print("=" * 70)
    
    # Step 1: Fetch profile
    print("\n📥 Fetching GitHub profile...")
    html = fetch_github_profile(username)
    if not html:
        print("❌ Failed to fetch profile")
        return
    print("✅ Profile fetched successfully")
    
    # Step 2: Extract colors
    print("\n🎨 Extracting contribution colors...")
    colors = extract_contribution_colors(html)
    if not colors:
        print("❌ No colors detected")
        return
    
    print(f"✅ Detected {len(colors)} unique colors:")
    for i, color in enumerate(colors[:15], 1):  # Show first 15
        print_color_box(color)
        if i % 5 == 0:
            print()  # New line every 5 colors
    print("\n")
    
    if len(colors) > 15:
        print(f"... and {len(colors) - 15} more colors\n")
    
    # Step 3: Detect theme
    print("🎃 Detecting holiday theme...")
    theme = detect_holiday_theme(colors)
    
    if not theme:
        print("ℹ️  No holiday theme detected (using default GitHub colors)")
        return
    
    print(f"✅ Holiday theme detected!")
    print(f"   Name: {theme['name']}")
    print(f"   Description: {theme['description']}")
    
    # Step 4: Generate schemes
    print("\n🌈 Generating color schemes...\n")
    
    light_scheme = generate_color_scheme(theme, mode='light')
    dark_scheme = generate_color_scheme(theme, mode='dark')
    
    # Display light scheme
    print("☀️  Light Theme:")
    print(f"   Snake: ", end="")
    print_color_box(light_scheme['snake'], "🐍")
    print()
    print(f"   Dots:  ", end="")
    for dot_color in light_scheme['dots']:
        print_color_box(dot_color)
    print("\n")
    
    # Display dark scheme
    print("🌙 Dark Theme:")
    print(f"   Snake: ", end="")
    print_color_box(dark_scheme['snake'], "🐍")
    print()
    print(f"   Dots:  ", end="")
    for dot_color in dark_scheme['dots']:
        print_color_box(dot_color)
    print("\n")
    
    # Output JSON
    print("=" * 70)
    print("\n📄 JSON Output:\n")
    result = {
        'holiday_detected': True,
        'theme_name': theme['name'],
        'theme_description': theme['description'],
        'light_color': light_scheme['snake'],
        'dark_color': dark_scheme['snake'],
        'light_dots': ', '.join(light_scheme['dots']),
        'dark_dots': ', '.join(dark_scheme['dots']),
        'all_colors': theme['colors'][:10],  # First 10 for readability
    }
    print(json.dumps(result, indent=2))
    print()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
