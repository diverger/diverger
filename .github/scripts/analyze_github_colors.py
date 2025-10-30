#!/usr/bin/env python3
"""
Quick script to analyze GitHub contribution graph colors
"""

import requests
import re
from bs4 import BeautifulSoup

username = 'diverger'

# Fetch the contribution fragment
url = f"https://github.com/{username}?action=show&controller=profiles&tab=contributions&user_id={username}"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}

print(f"Fetching: {url}")
response = requests.get(url, headers=headers, timeout=15)
print(f"Status: {response.status_code}")
print(f"Size: {len(response.text)} bytes")

# Save to file for inspection
with open('github_fragment.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Saved to github_fragment.html")

# Extract all hex colors
all_colors = re.findall(r'#[0-9a-fA-F]{6}', response.text)
unique_colors = sorted(set(all_colors))

print(f"\nFound {len(unique_colors)} unique colors:")
for color in unique_colors:
    print(f"  {color}")

# Look for specific patterns
soup = BeautifulSoup(response.text, 'html.parser')

# Try to find SVG
svgs = soup.find_all('svg')
print(f"\nFound {len(svgs)} SVG elements")

# Look for rects
rects = soup.find_all('rect')
print(f"Found {len(rects)} rect elements")

if rects:
    print("Sample rect attributes:")
    for i, rect in enumerate(rects[:5]):
        print(f"  Rect {i}: {rect.attrs}")

# Look for tool-tip or data attributes that might have colors
elements_with_data = soup.find_all(attrs={'data-level': True})
print(f"\nFound {len(elements_with_data)} elements with data-level")

# Search for "Halloween" or special themes
if 'halloween' in response.text.lower():
    print("\n✓ Found 'halloween' in the page!")
if 'happy halloween' in response.text.lower():
    print("✓ Found 'Happy Halloween' in the page!")

# Look for calendar-related colors in CSS/style
style_tags = soup.find_all('style')
print(f"\nFound {len(style_tags)} style tags")
if style_tags:
    for i, style in enumerate(style_tags):
        content = str(style.string) if style.string else ''
        calendar_refs = re.findall(r'calendar.*?color[^;]+', content, re.IGNORECASE)
        if calendar_refs:
            print(f"Style tag {i} calendar colors: {calendar_refs[:3]}")

print("\nDone! Check github_fragment.html for full content")
