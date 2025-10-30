# GitHub Holiday Color Detection

This script automatically detects when GitHub uses special holiday color schemes for the contribution graph and applies those colors to your snake animation.

## How It Works

1. **Detection**: The script fetches your GitHub profile and extracts the actual colors being used in the contribution graph
2. **Theme Recognition**: It identifies known holiday themes (Halloween, Christmas, Lunar New Year, Pride Month, etc.)
3. **Color Extraction**: Extracts the color palette and generates appropriate snake and dot colors
4. **Fallback**: If no holiday theme is detected, it uses your custom color schemes based on time/day

## Supported Holiday Themes

- 🎃 **Halloween** (October): Orange & Black theme
- 🎄 **Christmas** (December): Red & Green theme
- 🧧 **Lunar New Year** (Jan-Feb): Red & Gold theme
- 🏳️‍🌈 **Pride Month** (June): Rainbow theme
- 🎉 **Custom Events**: Automatically detects any special GitHub theme

## Workflow Integration

The workflow now includes these steps:

1. **Detect Holiday Colors** - Scrapes GitHub for current color scheme
2. **Set Color Scheme** - Uses holiday colors if detected, otherwise falls back to custom schemes
3. **Generate Snake** - Creates SVG with the selected colors

## Manual Testing

You can test the detector locally:

```bash
# Install dependencies
pip install requests beautifulsoup4 lxml

# Run the detector
python .github/scripts/detect_github_holiday_colors.py [username]

# Check the output
cat holiday_colors.json
```

## Output Format

The script outputs:

```json
{
  "holiday_detected": true,
  "theme_name": "halloween",
  "theme_description": "Halloween Theme (Orange & Black)",
  "light_color": "#FF8C00",
  "dark_color": "#FFA500",
  "light_dots": "#FFE4B5, #FFA500, #FF8C00, #FF6347, #8B4513",
  "dark_dots": "#000000, #8B4513, #FF6347, #FF8C00, #FFA500",
  "all_colors": ["#000000", "#8B4513", "#FF6347", "#FF8C00", "#FFA500"]
}
```

## Customization

To add more holiday patterns, edit the `holiday_patterns` dict in `detect_github_holiday_colors.py`:

```python
holiday_patterns = {
    'your_holiday': {
        'colors': ['#COLOR1', '#COLOR2', '#COLOR3'],
        'date_range': (month_start, day_start, month_end, day_end),
        'description': 'Your Holiday Theme',
    },
}
```

## Notes

- The detection runs automatically on every workflow execution
- Colors are extracted in real-time from GitHub's live contribution graph
- If GitHub changes their holiday theme mid-day, the next workflow run will pick it up
- The script is designed to be resilient - if detection fails, it falls back to custom schemes
