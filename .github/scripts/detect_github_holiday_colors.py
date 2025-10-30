#!/usr/bin/env python3
"""
GitHub Holiday Color Scheme Detector (Multi-method)

Detects GitHub's holiday color scheme using:
1. Live DOM color extraction (Primer CSS detection)
2. HTML message detection
3. Date-based fallback
"""

import os
import sys
import json
from datetime import datetime
from zoneinfo import ZoneInfo


# Primer CSS Default Colors (Fallback)
PRIMER_COLORS = {
    'light': {
        'level0': '#ebedf0',
        'level1': '#9be9a8',
        'level2': '#40c463',
        'level3': '#30a14e',
        'level4': '#216e39'
    },
    'dark': {
        'level0': '#161b22',
        'level1': '#0e4429',
        'level2': '#006d32',
        'level3': '#26a641',
        'level4': '#39d353'
    }
}


def extract_colors_from_dom(username):
    """
    Extract actual colors from GitHub contribution calendar DOM.
    Looks for CSS variables, style tags, and inline styles.
    Returns dict with colors or None if failed.
    """
    try:
        import urllib.request
        import re

        url = f'https://github.com/{username}'
        print(f"Fetching DOM from {url}...")

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')

        level_colors = {}

        # Method 1: Look for CSS variables in style tags (--color-calendar-graph-day-L0-bg, etc.)
        css_var_pattern = r'--color-calendar-graph-day-L(\d)-bg:\s*([#a-fA-F0-9]{6,7})'
        css_matches = re.findall(css_var_pattern, html)
        for level, color in css_matches:
            level = int(level)
            if level not in level_colors:
                level_colors[level] = color.lower() if color.startswith('#') else f'#{color.lower()}'

        if len(level_colors) >= 4:
            print(f"✓ Extracted {len(level_colors)} color levels from CSS variables")
            print(f"  Colors: {level_colors}")
            return level_colors

        # Method 2: Look for data-level with inline fill or style attributes
        patterns = [
            r'data-level="(\d)"[^>]*fill="([#\w]+)"',
            r'data-level="(\d)"[^>]*style="[^"]*fill:\s*([#\w]+)',
            r'fill="([#\w]+)"[^>]*data-level="(\d)"',
            r'<rect[^>]*data-level="(\d)"[^>]*class="[^"]*"[^>]*style="[^"]*background[^:]*:\s*([#\w]+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    if match[0].isdigit():
                        level, color = match
                    else:
                        color, level = match

                    level = int(level)
                    if level not in level_colors and color.startswith('#'):
                        level_colors[level] = color.lower()

        if len(level_colors) >= 4:
            print(f"✓ Extracted {len(level_colors)} color levels from DOM attributes")
            print(f"  Colors: {level_colors}")
            return level_colors

        # Method 3: Look for any contribution calendar color definitions in <style> tags
        style_pattern = r'\.ContributionCalendar-day\[data-level="(\d)"\][^}]*(?:background-color|fill):\s*([#a-fA-F0-9]{6,7})'
        style_matches = re.findall(style_pattern, html)
        for level, color in style_matches:
            level = int(level)
            if level not in level_colors:
                level_colors[level] = color.lower() if color.startswith('#') else f'#{color.lower()}'

        if len(level_colors) >= 4:
            print(f"✓ Extracted {len(level_colors)} color levels from style tags")
            print(f"  Colors: {level_colors}")
            return level_colors

        print(f"✗ Could not extract enough color levels from DOM (found {len(level_colors)} levels)")
        if level_colors:
            print(f"  Partial colors found: {level_colors}")
        return None

    except Exception as e:
        print(f"DOM extraction failed: {e}")
        return None


def analyze_colors_for_theme(colors):
    """
    Analyze extracted colors to detect which holiday theme they match.
    Returns theme name or None.
    """
    if not colors or len(colors) < 3:
        return None

    # Convert all colors to lowercase for comparison
    color_values = [c.lower() for c in colors.values()]
    color_str = ' '.join(color_values)

    # Halloween: Orange tones (#fb8500, #d47100, #bc4c00, #953800)
    halloween_markers = ['fb85', 'd471', 'bc4c', 'f60', 'fa0']
    if any(marker in color_str for marker in halloween_markers):
        print("✓ Color analysis: Detected Halloween theme (orange tones)")
        return 'halloween'

    # Christmas: Mix of red and green
    has_red = any(c in color_str for c in ['cf22', 'a40e', 'cf2', 'd41'])
    has_green = any(c in color_str for c in ['1a7f', '1163', '0a6', '0d4'])
    if has_red and has_green:
        print("✓ Color analysis: Detected Christmas theme (red & green)")
        return 'christmas'

    # Pink/Purple themes (Valentine's, Pride, Lunar New Year)
    has_pink = any(c in color_str for c in ['bf39', 'bf3', 'ea4a'])
    has_purple = any(c in color_str for c in ['8250', '622c', '845'])

    if has_pink or has_purple:
        month = datetime.now(ZoneInfo('UTC')).month
        if month == 2:
            print("✓ Color analysis: Detected Valentine's theme (pink/purple in Feb)")
            return 'valentines'
        elif month in (1, 2):
            print("✓ Color analysis: Detected Lunar New Year theme (pink/purple in Jan/Feb)")
            return 'lunar_new_year'
        elif month == 6:
            print("✓ Color analysis: Detected Pride theme (rainbow colors in June)")
            return 'pride'

    print("✗ Colors don't match known holiday themes")
    return None


def detect_holiday_from_html(username):
    """
    Fetch GitHub profile HTML and look for holiday messages or color attributes.
    Returns holiday name or None.
    """
    try:
        import urllib.request
        import re

        url = f'https://github.com/{username}'
        print(f"Fetching HTML from {url}...")

        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')

        # Method 1: Look for holiday messages in HTML
        holiday_patterns = {
            'halloween': ['Happy Halloween!', 'halloween'],
            'christmas': ['Happy Holidays!', 'Merry Christmas!', 'Season\'s Greetings'],
            'lunar_new_year': ['Happy Lunar New Year!', 'Lunar New Year'],
            'valentines': ['Happy Valentine\'s Day!', 'Valentine\'s Day', 'valentine'],
            'pride': ['Happy Pride!', 'Pride Month']
        }

        html_lower = html.lower()

        for holiday, patterns in holiday_patterns.items():
            for pattern in patterns:
                if pattern.lower() in html_lower:
                    print(f"✓ Found '{pattern}' in HTML")
                    return holiday

        # Method 2: Look for data-level attributes with non-standard colors
        # GitHub dynamically injects holiday colors via data attributes
        level_elements = re.findall(r'data-level="[0-4]"[^>]*style="[^"]*background-color:\s*([#a-fA-F0-9]{6,7})', html)

        if level_elements:
            colors = set(level_elements[:20])  # Get first 20 unique colors
            print(f"Found {len(colors)} contribution colors: {list(colors)[:5]}")

            # Analyze colors to detect holiday
            colors_lower = [c.lower() for c in colors]

            # Halloween: orange tones (fb, d4, bc, 95, 76)
            if any(c.startswith('#fb') or c.startswith('#d4') or c.startswith('#bc') for c in colors_lower):
                if any('8500' in c or '7100' in c or '4c00' in c for c in colors_lower):
                    print("✓ Detected Halloween colors (orange tones)")
                    return 'halloween'

            # Valentine's/Pride: pink/purple (bf, 82, 62)
            if any(c.startswith('#bf') or c.startswith('#82') or c.startswith('#62') for c in colors_lower):
                if any('3989' in c or '50df' in c or '2cbc' in c for c in colors_lower):
                    # Check date to distinguish valentine vs pride
                    from datetime import datetime
                    month = datetime.now().month
                    if month == 2:
                        print("✓ Detected Valentine's colors (pink/purple)")
                        return 'valentines'
                    elif month == 6:
                        print("✓ Detected Pride colors (rainbow)")
                        return 'pride'

            # Christmas: red and green mix
            has_red = any(c.startswith('#cf') or c.startswith('#a4') for c in colors_lower)
            has_green = any(c.startswith('#1a') or c.startswith('#11') for c in colors_lower)
            if has_red and has_green:
                print("✓ Detected Christmas colors (red & green)")
                return 'christmas'

        print("✗ No holiday theme detected in HTML")
        return None

    except Exception as e:
        print(f"HTML fetch failed: {e}")
        return None


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
        'valentines': {
            'start': (2, 10),
            'end': (2, 14),
            'description': 'Valentine\'s Day'
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
    """Create predefined color theme from holiday name using GitHub Primer colors."""
    themes = {
        'halloween': {
            'light_color': '#fb8500',
            'dark_color': '#d47100',
            'light_dots': '#fb8500, #d47100, #bc4c00, #953800, #762d0a',
            'dark_dots': '#d47100, #bc4c00, #953800, #762d0a, #5a1e02',
            'description': 'Halloween Theme (Orange)'
        },
        'christmas': {
            'light_color': '#1a7f37',
            'dark_color': '#cf222e',
            'light_dots': '#1a7f37, #116329, #0969da, #0550ae, #cf222e',
            'dark_dots': '#116329, #0550ae, #0969da, #8250df, #a40e26',
            'description': 'Christmas Theme (Green & Red)'
        },
        'lunar_new_year': {
            'light_color': '#bf3989',
            'dark_color': '#cf222e',
            'light_dots': '#bf3989, #8250df, #cf222e, #a40e26, #82071e',
            'dark_dots': '#8250df, #a40e26, #82071e, #6e011a, #540719',
            'description': 'Lunar New Year (Pink & Red)'
        },
        'valentines': {
            'light_color': '#bf3989',
            'dark_color': '#8250df',
            'light_dots': '#bf3989, #8250df, #cf222e, #fb8500, #a40e26',
            'dark_dots': '#8250df, #a40e26, #82071e, #6e011a, #622cbc',
            'description': 'Valentine\'s Day (Pink & Purple)'
        },
        'pride': {
            'light_color': '#0969da',
            'dark_color': '#8250df',
            'light_dots': '#cf222e, #fb8500, #d4a72c, #1a7f37, #0969da',
            'dark_dots': '#a40e26, #d47100, #9a6700, #116329, #622cbc',
            'description': 'Pride Month (Rainbow)'
        },
    }

    return themes.get(theme_name)



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
    print(f"Timestamp: {datetime.now(ZoneInfo('UTC')).isoformat()}")

    # Method 1: Extract live colors from DOM (most accurate)
    print("\n=== Method 1: Live DOM color extraction ===")
    dom_colors = extract_colors_from_dom(username)

    if dom_colors:
        # Analyze extracted colors to detect theme
        theme_name = analyze_colors_for_theme(dom_colors)
        if theme_name:
            print(f"✓ Detected {theme_name} theme from live colors")
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
                    'detection_method': 'dom-colors',
                    'extracted_colors': str(dom_colors)
                }
                output_result(result)
                return

    # Method 2: Check HTML for holiday messages
    print("\n=== Method 2: HTML message detection ===")
    holiday_name = detect_holiday_from_html(username)

    if holiday_name:
        print(f"✓ Detected {holiday_name} from HTML message")
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
                'detection_method': 'html-message'
            }
            output_result(result)
            return

    # Method 3: Date-based detection as fallback
    print("\n=== Method 3: Date-based holiday detection ===")
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
