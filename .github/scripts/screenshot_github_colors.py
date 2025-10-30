#!/usr/bin/env python3
"""
Screenshot GitHub contribution graph and extract colors
Uses Playwright for browser automation
"""

import sys
import json
from collections import Counter

try:
    from playwright.sync_api import sync_playwright
    from PIL import Image
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "Pillow"])
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    from playwright.sync_api import sync_playwright
    from PIL import Image


def capture_contribution_graph(username, output_file='contribution_graph.png'):
    """Capture screenshot of GitHub contribution graph."""
    print(f"Opening browser to capture {username}'s contribution graph...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate to user profile
        url = f'https://github.com/{username}'
        print(f"Loading {url}")
        page.goto(url, wait_until='networkidle')
        
        # Wait for contribution graph to load
        page.wait_for_selector('svg.js-calendar-graph-svg', timeout=10000)
        
        # Find the contribution graph element
        contribution_element = page.locator('.js-yearly-contributions')
        
        # Take screenshot of just the contribution area
        contribution_element.screenshot(path=output_file)
        print(f"Screenshot saved to {output_file}")
        
        browser.close()
    
    return output_file


def extract_colors_from_image(image_path, max_colors=10):
    """Extract dominant colors from contribution graph screenshot."""
    print(f"\nAnalyzing colors from {image_path}...")
    
    # Open image
    img = Image.open(image_path)
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Get all pixels
    pixels = list(img.getdata())
    
    # Count color frequencies
    color_counts = Counter(pixels)
    
    # Filter out white/near-white background colors
    filtered_colors = {
        color: count for color, count in color_counts.items()
        if not (color[0] > 240 and color[1] > 240 and color[2] > 240)  # Skip whites
        and not (color[0] < 30 and color[1] < 30 and color[2] < 30)    # Skip pure black backgrounds
    }
    
    # Get most common colors
    most_common = sorted(filtered_colors.items(), key=lambda x: x[1], reverse=True)[:max_colors]
    
    # Convert RGB to hex
    hex_colors = []
    for (r, g, b), count in most_common:
        hex_color = f'#{r:02X}{g:02X}{b:02X}'
        percentage = (count / len(pixels)) * 100
        hex_colors.append(hex_color)
        print(f"  {hex_color} - {count:6d} pixels ({percentage:5.2f}%)")
    
    return hex_colors


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else 'diverger'
    
    print(f"=== GitHub Contribution Graph Color Extractor ===\n")
    
    # Step 1: Capture screenshot
    screenshot_file = capture_contribution_graph(username)
    
    # Step 2: Extract colors from screenshot
    colors = extract_colors_from_image(screenshot_file)
    
    # Step 3: Output results
    print(f"\n=== Extracted {len(colors)} colors ===")
    result = {
        'username': username,
        'colors': colors,
        'screenshot': screenshot_file,
    }
    
    # Save to JSON
    with open('extracted_colors.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\nResults saved to extracted_colors.json")
    print(f"Colors: {colors}")
    
    return colors


if __name__ == '__main__':
    main()
