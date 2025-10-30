#!/usr/bin/env python3
"""
GitHub Holiday Color Scheme Detector (Screenshot-based)

Detects GitHub's holiday color scheme using screenshot analysis and date-based detection.
"""

import os
import sys
import json
from datetime import datetime
from zoneinfo import ZoneInfo


def capture_and_extract_colors(username):
    """
    Capture screenshot of contribution graph and extract colors.
    Returns list of hex colors or None if failed.
    """
    try:
        from playwright.sync_api import sync_playwright
        from PIL import Image
        from collections import Counter
    except ImportError:
        print("Playwright/Pillow not available, skipping screenshot method")
        return None

    try:
        print("Attempting screenshot-based color extraction...")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1920, 'height': 1080})

            url = f'https://github.com/{username}'
            page.goto(url, wait_until='networkidle', timeout=30000)
            page.wait_for_selector('.js-yearly-contributions', timeout=10000)

            # Screenshot the contribution area
            contribution_element = page.locator('.js-yearly-contributions')
            screenshot_path = 'temp_contribution_graph.png'
            contribution_element.screenshot(path=screenshot_path)

            browser.close()

            # Extract colors from screenshot
            img = Image.open(screenshot_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            pixels = list(img.getdata())
            color_counts = Counter(pixels)

            # Filter out backgrounds (white and very dark)
            filtered_colors = {
                color: count for color, count in color_counts.items()
                if not (color[0] > 240 and color[1] > 240 and color[2] > 240)
                and not (color[0] < 20 and color[1] < 20 and color[2] < 20)
            }

            # Get top 10 colors
            most_common = sorted(filtered_colors.items(), key=lambda x: x[1], reverse=True)[:10]

            hex_colors = [f'#{r:02X}{g:02X}{b:02X}' for (r, g, b), _ in most_common]

            print(f"✓ Extracted {len(hex_colors)} colors via screenshot: {hex_colors[:5]}")

            # Clean up
            import os
            if os.path.exists(screenshot_path):
                os.remove(screenshot_path)

            return hex_colors

    except Exception as e:
        print(f"Screenshot method failed: {e}")
        return None


def is_orange_ish(hex_color):
    """Check if color is orange-ish."""
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
    r, g, b = rgb
    return r > 200 and g > 100 and g < r and b < g


def is_red_ish(hex_color):
    """Check if color is red-ish."""
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
    r, g, b = rgb
    return r > 150 and r > g * 1.5 and r > b * 1.5


def is_green_ish(hex_color):
    """Check if color is green-ish."""
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
    r, g, b = rgb
    return g > 150 and g > r * 1.3 and g > b


def is_dark_color(hex_color):
    """Check if color is dark."""
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
    return sum(rgb) < 150


def check_holiday_by_date(current_date=None):
    """
    Check if current date falls within a known holiday period.
    Returns holiday name or None.
    """
    if current_date is None:
        current_date = datetime.now(ZoneInfo('UTC'))

    month = current_date.month
    day = current_date.day

    # Define holiday date ranges
    holidays = {
        'halloween': {
            'start': (10, 25),
            'end': (11, 1),
            'description': 'Halloween'
        },
        'christmas': {
            'start': (12, 1),
            'end': (12, 31),
            'description': 'Christmas Season'
        },
        'lunar_new_year': {
            'start': (1, 20),
            'end': (2, 20),
            'description': 'Lunar New Year'
        },
        'pride': {
            'start': (6, 1),
            'end': (6, 30),
            'description': 'Pride Month'
        },
    }

    for holiday_name, holiday_data in holidays.items():
        start_month, start_day = holiday_data['start']
        end_month, end_day = holiday_data['end']

        if start_month == end_month:
            if month == start_month and start_day <= day <= end_day:
                return holiday_name
        else:
            if (month == start_month and day >= start_day) or \
               (month == end_month and day <= end_day):
                return holiday_name

    return None


def create_theme_from_name(theme_name):
    """Create predefined color theme from holiday name."""
    themes = {
        'halloween': {
            'light_color': '#FFD700',
            'dark_color': '#FFA500',
            'light_dots': '#FFD700, #FFA500, #FF8C00, #FF6347, #8B4513',
            'dark_dots': '#FF4500, #FF7F00, #FFA07A, #CD5C5C, #8B0000',
            'description': 'Halloween Theme (Orange & Black)'
        },
        'christmas': {
            'light_color': '#FF0000',
            'dark_color': '#00FF00',
            'light_dots': '#FF0000, #DC143C, #FFD700, #00FF00, #228B22',
            'dark_dots': '#8B0000, #B22222, #FFD700, #006400, #2E8B57',
            'description': 'Christmas Theme (Red & Green)'
        },
        'lunar_new_year': {
            'light_color': '#FFD700',
            'dark_color': '#FF0000',
            'light_dots': '#FFD700, #FFA500, #FF0000, #DC143C, #FF6347',
            'dark_dots': '#B8860B, #FF8C00, #8B0000, #B22222, #CD5C5C',
            'description': 'Lunar New Year (Gold & Red)'
        },
        'pride': {
            'light_color': '#FF0000',
            'dark_color': '#800080',
            'light_dots': '#FF0000, #FFA500, #FFFF00, #008000, #0000FF',
            'dark_dots': '#8B0000, #FF8C00, #9ACD32, #006400, #00008B',
            'description': 'Pride Month (Rainbow)'
        },
    }

    return themes.get(theme_name)


def detect_holiday_theme(colors):
    """
    Analyze extracted colors to detect holiday theme.
    Returns dict with theme info or None.
    """
    if not colors or len(colors) < 3:
        return None

    # Halloween detection: orange + dark colors
    has_orange = any(is_orange_ish(c) for c in colors)
    has_dark = any(is_dark_color(c) for c in colors)

    if has_orange and has_dark:
        return 'halloween'

    # Christmas detection: red + green
    has_red = any(is_red_ish(c) for c in colors)
    has_green = any(is_green_ish(c) for c in colors)

    if has_red and has_green:
        return 'christmas'

    return None


def output_result(result):
    """Output result in GitHub Actions format."""
    # Set output for GitHub Actions
    github_output = os.environ.get('GITHUB_OUTPUT')

    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            for key, value in result.items():
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                f.write(f"{key}={value}\n")

    # Also print as JSON for logging
    print("\n=== Detection Result ===")
    print(json.dumps(result, indent=2))


def main():
    """Main execution function."""
    username = os.environ.get('GITHUB_USERNAME', 'diverger')
    if len(sys.argv) > 1:
        username = sys.argv[1]

    print(f"Detecting holiday theme for GitHub user: {username}")

    # Method 1: Try screenshot-based extraction
    print("\n=== Method 1: Screenshot-based color extraction ===")
    colors = capture_and_extract_colors(username)

    if colors:
        theme_name = detect_holiday_theme(colors)
        if theme_name:
            print(f"✓ Detected {theme_name} theme from screenshot!")
            theme = create_theme_from_name(theme_name)
            if theme:
                result = {
                    'holiday_detected': True,
                    'theme_name': theme_name,
                    'theme_description': theme['description'],
                    'light_color': theme['light_color'],
                    'dark_color': theme['dark_color'],
                    'light_dots': theme['light_dots'],
                    'dark_dots': theme['dark_dots'],
                    'detection_method': 'screenshot'
                }
                output_result(result)
                return

    # Method 2: Date-based detection as fallback
    print("\n=== Method 2: Date-based holiday detection ===")
    holiday_name = check_holiday_by_date()

    if holiday_name:
        print(f"✓ Current date matches {holiday_name} period")
        theme = create_theme_from_name(holiday_name)
        if theme:
            result = {
                'holiday_detected': True,
                'theme_name': holiday_name,
                'theme_description': theme['description'],
                'light_color': theme['light_color'],
                'dark_color': theme['dark_color'],
                'light_dots': theme['light_dots'],
                'dark_dots': theme['dark_dots'],
                'detection_method': 'date'
            }
            output_result(result)
            return

    # No holiday detected
    print("\n✗ No holiday theme detected")
    result = {
        'holiday_detected': False,
        'theme_name': 'default',
        'light_color': '#9BE9A8',
        'dark_color': '#40C463',
        'light_dots': '#9BE9A8, #40C463, #30A14E, #216E39',
        'dark_dots': '#0E4429, #006D32, #26A641, #39D353',
        'detection_method': 'none'
    }
    output_result(result)


if __name__ == '__main__':
    main()
