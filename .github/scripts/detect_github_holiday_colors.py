#!/usr/bin/env python3
"""
GitHub Holiday Color Scheme Detector

Detects if GitHub is using a special holiday color scheme for the contribution graph
and extracts those colors for use in the snake animation.
"""

import os
import sys
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "beautifulsoup4", "lxml"])
    import requests
    from bs4 import BeautifulSoup


def fetch_github_profile(username):
    """Fetch GitHub profile page to analyze contribution graph colors."""
    url = f"https://github.com/{username}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"Fetched {len(response.text)} bytes from GitHub profile")
        return response.text
    except Exception as e:
        print(f"Error fetching GitHub profile: {e}", file=sys.stderr)
        return None


def fetch_contribution_graph_data(username):
    """Fetch contribution graph SVG directly from GitHub's graph API."""
    # GitHub provides an SVG endpoint for the contribution graph
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        print(f"Fetched contribution graph: {len(response.text)} bytes")
        return response.text
    except Exception as e:
        print(f"Error fetching contribution graph: {e}", file=sys.stderr)
        return None


def detect_holiday_message(html_content):
    """
    Detect holiday message from GitHub contribution graph.
    GitHub often displays messages like "Happy Halloween" during holidays.
    Returns holiday name if detected, None otherwise.
    """
    if not html_content:
        return None

    # Convert to lowercase for case-insensitive matching
    content_lower = html_content.lower()

    # Define holiday message patterns
    holiday_messages = {
        'halloween': ['happy halloween', 'halloween', '🎃', 'trick or treat'],
        'christmas': ['merry christmas', 'happy holidays', 'season\'s greetings', '🎄', '🎅'],
        'lunar_new_year': ['happy lunar new year', 'happy new year', 'lunar new year', '🧧', '🐉'],
        'valentines': ['happy valentine', 'valentine\'s day', '💝', '❤️'],
        'pride': ['happy pride', 'pride month', '🏳️‍🌈'],
        'thanksgiving': ['happy thanksgiving', 'thanksgiving', '🦃'],
        'new_year': ['happy new year', '🎆', '🎊'],
    }

    print("\n=== Checking for holiday messages ===")
    for holiday, patterns in holiday_messages.items():
        for pattern in patterns:
            if pattern in content_lower:
                print(f"✓ Found holiday message: '{pattern}' -> {holiday}")
                return holiday

    print("No holiday message detected")
    return None
def extract_contribution_colors(html_content, is_graph_svg=False):
    """
    Extract contribution graph colors from GitHub profile HTML or SVG.
    Returns a list of detected colors or None if using default colors.
    """
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, 'html.parser')

    colors = set()

    # If this is the direct contribution graph SVG
    if is_graph_svg:
        # Extract all rect elements with fill colors
        rects = soup.find_all('rect')
        print(f"Found {len(rects)} rect elements in contribution graph")

        for rect in rects:
            fill = rect.get('fill', '')
            style = rect.get('style', '')

            if fill and fill.startswith('#'):
                colors.add(fill.upper())
            elif 'fill:' in style:
                color_match = re.search(r'fill:\s*(#[0-9a-fA-F]{6})', style)
                if color_match:
                    colors.add(color_match.group(1).upper())

        # Also check for colors in class definitions
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            if style_tag.string:
                color_matches = re.findall(r'fill:\s*(#[0-9a-fA-F]{6})', style_tag.string)
                colors.update([c.upper() for c in color_matches])
    else:
        # Extract from full profile page
        # Method 1: Find contribution graph SVG elements
        contribution_cells = soup.find_all('rect', {'data-level': True})

        if not contribution_cells:
            # Try alternative selectors for contribution cells
            contribution_cells = soup.select('[data-date]')

        if not contribution_cells:
            # Try finding any rect in svg with class containing "ContributionCalendar"
            contribution_cells = soup.select('svg.js-calendar-graph-svg rect, svg.ContributionCalendar-day')

        print(f"Found {len(contribution_cells)} contribution cells")

        for cell in contribution_cells:
            # Extract fill color from style or fill attribute
            style = cell.get('style', '')
            fill = cell.get('fill', '')

            if 'fill:' in style:
                color_match = re.search(r'fill:\s*(#[0-9a-fA-F]{6})', style)
                if color_match:
                    colors.add(color_match.group(1).upper())
            elif fill and fill.startswith('#'):
                colors.add(fill.upper())
            elif fill and fill.startswith('var('):
                # Handle CSS variables like var(--color-calendar-graph-day-L1-bg)
                continue

        # Method 2: Look for CSS custom properties in style tags
        style_tags = soup.find_all('style')
        for style_tag in style_tags:
            if style_tag.string:
                # Look for calendar-specific color definitions
                # e.g., --color-calendar-graph-day-L4-bg: #ff8c00;
                calendar_colors = re.findall(
                    r'--color-calendar[^:]*:\s*(#[0-9a-fA-F]{6})',
                    style_tag.string
                )
                colors.update([c.upper() for c in calendar_colors])

        # Method 3: Check for inline SVG styles
        svgs = soup.find_all('svg')
        for svg in svgs:
            svg_string = str(svg)
            if 'calendar' in svg_string.lower() or 'contribution' in svg_string.lower():
                svg_colors = re.findall(r'fill=["\']?(#[0-9a-fA-F]{6})', svg_string)
                colors.update([c.upper() for c in svg_colors])

    print(f"Extracted {len(colors)} unique colors")
    if colors:
        print(f"Sample colors: {list(sorted(colors))[:10]}")

    return list(sorted(colors)) if colors else None


def create_theme_from_name(holiday_name):
    """Create a theme dict from a holiday name using predefined colors."""
    holiday_colors = {
        'halloween': {
            'name': 'halloween',
            'description': 'Halloween Theme (Orange & Black)',
            'colors': ['#000000', '#8B4513', '#FF6347', '#FF8C00', '#FFA500', '#FFD700'],
        },
        'christmas': {
            'name': 'christmas',
            'description': 'Christmas Theme (Red & Green)',
            'colors': ['#006400', '#228B22', '#DC143C', '#FF0000', '#FFD700', '#FFFFFF'],
        },
        'lunar_new_year': {
            'name': 'lunar_new_year',
            'description': 'Lunar New Year Theme (Red & Gold)',
            'colors': ['#8B0000', '#DC143C', '#FF0000', '#FF6347', '#FFD700', '#FFA500'],
        },
        'pride': {
            'name': 'pride',
            'description': 'Pride Month Theme (Rainbow)',
            'colors': ['#FF0000', '#FFA500', '#FFFF00', '#008000', '#0000FF', '#800080'],
        },
        'valentines': {
            'name': 'valentines',
            'description': 'Valentine\'s Day Theme (Pink & Red)',
            'colors': ['#FF1493', '#FF69B4', '#FFB6C1', '#DC143C', '#FF0000'],
        },
    }

    return holiday_colors.get(holiday_name)


def create_theme_from_colors_and_name(colors, holiday_name):
    """Create a theme using detected colors and holiday name."""
    descriptions = {
        'halloween': 'Halloween Theme (Orange & Black)',
        'christmas': 'Christmas Theme (Red & Green)',
        'lunar_new_year': 'Lunar New Year Theme (Red & Gold)',
        'pride': 'Pride Month Theme (Rainbow)',
        'valentines': 'Valentine\'s Day Theme (Pink & Red)',
    }

    return {
        'name': holiday_name,
        'description': descriptions.get(holiday_name, f'{holiday_name.title()} Theme'),
        'colors': colors,
    }


def is_orange_ish(hex_color):
    """Check if a color is orange-ish (high red, medium-high green, low blue)."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    # Orange: R > 200, G > 100, G < R, B < 150
    return r > 200 and 100 < g < r and b < 150


def is_dark_color(hex_color):
    """Check if a color is dark (low overall brightness)."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    brightness = (r + g + b) / 3
    return brightness < 80  # Dark if average < 80


def is_red_ish(hex_color):
    """Check if a color is red-ish (high red, low green and blue)."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return r > 150 and r > g * 1.5 and r > b * 1.5


def is_green_ish(hex_color):
    """Check if a color is green-ish (high green, lower red and blue)."""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return g > 150 and g > r * 1.2 and g > b * 1.2


def detect_holiday_theme(colors, current_date=None):
    """
    Detect if the colors match a known holiday theme.
    Returns theme name and metadata if detected.
    """
    if not colors or len(colors) < 3:
        return None

    if current_date is None:
        current_date = datetime.now(ZoneInfo('UTC'))

    # Define known holiday color patterns
    # These are approximate - you may need to update based on actual GitHub themes
    holiday_patterns = {
        'halloween': {
            'colors': ['#FFA500', '#FF8C00', '#FF6347', '#8B4513', '#000000',
                      '#FF4500', '#FF7F00', '#FFA07A', '#CD5C5C', '#8B0000'],
            'date_range': (10, 1, 11, 1),  # Oct 1 - Nov 1
            'description': 'Halloween Theme (Orange & Black)',
            'keywords': ['orange', 'dark', 'black'],  # Color themes to look for
        },
        'christmas': {
            'colors': ['#FF0000', '#00FF00', '#FFD700', '#FFFFFF', '#DC143C', '#228B22'],
            'date_range': (12, 1, 12, 31),  # Dec 1 - Dec 31
            'description': 'Christmas Theme (Red & Green)',
            'keywords': ['red', 'green'],
        },
        'lunar_new_year': {
            'colors': ['#FF0000', '#FFD700', '#FFA500', '#DC143C', '#FF6347'],
            'date_range': (1, 20, 2, 20),  # Approximate
            'description': 'Lunar New Year Theme (Red & Gold)',
            'keywords': ['red', 'gold'],
        },
        'pride': {
            'colors': ['#FF0000', '#FFA500', '#FFFF00', '#008000', '#0000FF', '#800080'],
            'date_range': (6, 1, 6, 30),  # June
            'description': 'Pride Month Theme (Rainbow)',
            'keywords': ['rainbow', 'multi'],
        },
    }

    # Check if current date matches any holiday period
    month = current_date.month
    day = current_date.day

    for theme_name, theme_data in holiday_patterns.items():
        start_m, start_d, end_m, end_d = theme_data['date_range']

        # Simple date range check
        in_range = False
        if start_m == end_m:
            in_range = month == start_m and start_d <= day <= end_d
        elif start_m < end_m:
            in_range = (month == start_m and day >= start_d) or \
                      (month == end_m and day <= end_d) or \
                      (start_m < month < end_m)
        else:  # Wraps around year end
            in_range = (month == start_m and day >= start_d) or \
                      (month == end_m and day <= end_d) or \
                      (month > start_m or month < end_m)

        if in_range:
            # Check if detected colors match theme colors (loose matching)
            theme_colors = set(theme_data['colors'])
            detected_colors = set(colors)

            # Direct overlap check
            overlap = len(theme_colors & detected_colors)
            if overlap >= 2:  # At least 2 matching colors
                return {
                    'name': theme_name,
                    'description': theme_data['description'],
                    'colors': colors,
                }

            # Color similarity check for theme
            # Check if detected colors are in similar color families
            if theme_name == 'halloween':
                # Look for orange-ish and dark colors
                has_orange = any(is_orange_ish(c) for c in detected_colors)
                has_dark = any(is_dark_color(c) for c in detected_colors)
                if has_orange and has_dark:
                    return {
                        'name': theme_name,
                        'description': theme_data['description'],
                        'colors': colors,
                    }
            elif theme_name == 'christmas':
                # Look for red and green colors
                has_red = any(is_red_ish(c) for c in detected_colors)
                has_green = any(is_green_ish(c) for c in detected_colors)
                if has_red and has_green:
                    return {
                        'name': theme_name,
                        'description': theme_data['description'],
                        'colors': colors,
                    }

    # If we have special colors but no theme match, it's likely a special event
    # GitHub default is typically: #ebedf0, #9be9a8, #40c463, #30a14e, #216e39 (light)
    # or #161b22, #0e4429, #006d32, #26a641, #39d353 (dark)
    default_light = {'#EBEDF0', '#9BE9A8', '#40C463', '#30A14E', '#216E39'}
    default_dark = {'#161B22', '#0E4429', '#006D32', '#26A641', '#39D353'}

    detected_set = set(colors)

    # If colors are very different from defaults, it's likely a special theme
    if len(detected_set & default_light) < 2 and len(detected_set & default_dark) < 2:
        return {
            'name': 'custom_holiday',
            'description': 'Special GitHub Theme Detected',
            'colors': colors,
        }

    return None


def generate_color_scheme(theme, mode='light'):
    """
    Generate a color scheme dict compatible with the existing workflow format.
    """
    if not theme or not theme.get('colors'):
        return None

    colors = theme['colors']

    # Sort colors by brightness for proper gradient
    def brightness(hex_color):
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        return sum(rgb) / 3

    sorted_colors = sorted(colors, key=brightness)

    # Ensure we have at least 5 colors for the dots gradient
    if len(sorted_colors) < 5:
        # Interpolate or repeat colors
        while len(sorted_colors) < 5:
            sorted_colors.append(sorted_colors[-1])

    # Select appropriate colors
    if mode == 'light':
        # Use lighter/brighter colors
        dots = sorted_colors[-5:] if len(sorted_colors) >= 5 else sorted_colors
        snake = sorted_colors[-1]  # Brightest
    else:
        # Use darker colors for background compatibility
        dots = sorted_colors[:5] if len(sorted_colors) >= 5 else sorted_colors
        if len(sorted_colors) > 5:
            snake = sorted_colors[len(sorted_colors)//2]  # Middle brightness
        else:
            snake = sorted_colors[-1]

    return {
        'style': theme.get('description', 'Holiday Theme'),
        'snake': snake,
        'dots': dots,
    }


def main():
    """Main execution function."""
    # Get username from environment or argument
    username = os.environ.get('GITHUB_USERNAME', 'diverger')
    if len(sys.argv) > 1:
        username = sys.argv[1]

    print(f"Checking GitHub profile for holiday theme: {username}")

    # Try method 1: Fetch contribution graph directly
    print("\n=== Method 1: Fetching contribution graph SVG ===")
    graph_html = fetch_contribution_graph_data(username)

    # Check for holiday message first (most reliable)
    holiday_from_message = detect_holiday_message(graph_html) if graph_html else None

    # Extract colors
    colors = extract_contribution_colors(graph_html, is_graph_svg=True) if graph_html else None

    # Try method 2: Fetch full profile page if needed
    if not colors and not holiday_from_message:
        print("\n=== Method 2: Fetching full profile page ===")
        html = fetch_github_profile(username)
        holiday_from_message = detect_holiday_message(html) if html and not holiday_from_message else holiday_from_message
        colors = extract_contribution_colors(html, is_graph_svg=False) if html else None

    # If we found a holiday message but no colors, try to use predefined colors for that holiday
    if holiday_from_message and not colors:
        print(f"\n✓ Holiday detected from message: {holiday_from_message}")
        print("Using predefined holiday colors")
        theme = create_theme_from_name(holiday_from_message)
        if theme:
            light_scheme = generate_color_scheme(theme, mode='light')
            dark_scheme = generate_color_scheme(theme, mode='dark')

            result = {
                'holiday_detected': True,
                'theme_name': holiday_from_message,
                'theme_description': theme['description'],
                'light_color': light_scheme['snake'],
                'dark_color': dark_scheme['snake'],
                'light_dots': ', '.join(light_scheme['dots']),
                'dark_dots': ', '.join(dark_scheme['dots']),
                'all_colors': theme['colors'],
                'detection_method': 'message',
            }
            output_result(result)
            return

    if not colors:
        print("Could not detect contribution colors, using default scheme")
        output_result({'holiday_detected': False})
        return

    print(f"\n✓ Detected {len(colors)} unique colors: {colors[:10]}...")  # Show first 10

    # Detect holiday theme from colors
    theme = detect_holiday_theme(colors)

    # If we detected a holiday from message, use that to help identify the theme
    if holiday_from_message and not theme:
        print(f"Creating theme based on message: {holiday_from_message}")
        theme = create_theme_from_colors_and_name(colors, holiday_from_message)

    if not theme:
        print("No special holiday theme detected")
        print(f"Current date: {datetime.now(ZoneInfo('UTC')).strftime('%Y-%m-%d')}")
        print("Checking if colors differ from defaults...")

        default_light = {'#EBEDF0', '#9BE9A8', '#40C463', '#30A14E', '#216E39'}
        default_dark = {'#161B22', '#0E4429', '#006D32', '#26A641', '#39D353'}
        detected_set = set(colors)

        light_match = len(detected_set & default_light)
        dark_match = len(detected_set & default_dark)
        print(f"Matches with default light: {light_match}/5")
        print(f"Matches with default dark: {dark_match}/5")

        output_result({'holiday_detected': False})
        return

    print(f"Holiday theme detected: {theme['description']}")
    print(f"Theme colors: {theme['colors']}")

    # Generate color schemes
    light_scheme = generate_color_scheme(theme, mode='light')
    dark_scheme = generate_color_scheme(theme, mode='dark')

    # Determine detection method
    detection_method = 'message' if holiday_from_message else 'colors'

    # Output results
    result = {
        'holiday_detected': True,
        'theme_name': theme['name'],
        'theme_description': theme['description'],
        'light_color': light_scheme['snake'],
        'dark_color': dark_scheme['snake'],
        'light_dots': ', '.join(light_scheme['dots']),
        'dark_dots': ', '.join(dark_scheme['dots']),
        'all_colors': theme['colors'],
        'detection_method': detection_method,
    }
    }

    output_result(result)


def output_result(result):
    """Output result to GitHub Actions output."""
    # Print to stdout for debugging
    print("\n=== Detection Result ===")
    print(json.dumps(result, indent=2))

    # Write to GitHub Actions output
    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            for key, value in result.items():
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                elif isinstance(value, (list, dict)):
                    value = json.dumps(value)
                # Escape newlines and percent signs for GitHub Actions
                value = str(value).replace('%', '%25').replace('\n', '%0A').replace('\r', '%0D')
                f.write(f"{key}={value}\n")

    # Also output as JSON for potential other uses
    output_file = os.environ.get('OUTPUT_JSON', 'holiday_colors.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nResults written to {output_file}")
if __name__ == '__main__':
    main()
