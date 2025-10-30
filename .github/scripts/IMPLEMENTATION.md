# GitHub Holiday Color Detection - Implementation Summary

## 📋 What Was Implemented

A complete system to automatically detect and use GitHub's special holiday color schemes for the contribution graph snake animation.

## 🗂️ Files Created/Modified

### New Files Created

1. **`.github/scripts/detect_github_holiday_colors.py`**
   - Main script that scrapes GitHub profiles
   - Detects holiday color schemes
   - Extracts and processes colors
   - Outputs results in GitHub Actions format

2. **`.github/scripts/test_holiday_detection.py`**
   - Interactive test script with colored terminal output
   - Visualizes detected colors
   - Useful for debugging and manual testing

3. **`.github/scripts/demo.sh`**
   - Quick demo script for testing
   - Handles dependency installation
   - Simple command-line interface

4. **`.github/scripts/requirements.txt`**
   - Python dependencies: requests, beautifulsoup4, lxml

5. **`.github/scripts/README.md`**
   - Comprehensive documentation
   - Usage instructions
   - Customization guide

### Modified Files

1. **`.github/workflows/snake.yml`**
   - Added Python setup step
   - Added dependency installation
   - Added holiday color detection step
   - Updated color scheme logic to prioritize holiday colors
   - Falls back to existing custom schemes when no holiday detected

2. **`README.md`**
   - Added section explaining the new holiday color feature
   - Linked to detailed documentation

## 🎯 How It Works

```
┌─────────────────────────────────────────┐
│  GitHub Actions Workflow Trigger        │
│  (hourly, push, or manual)              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  1. Checkout Repository                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  2. Setup Python & Install Dependencies │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  3. Detect GitHub Holiday Colors        │
│     - Fetch user's GitHub profile       │
│     - Extract contribution grid colors  │
│     - Detect holiday theme              │
│     - Generate color schemes            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  4. Set Color Scheme                    │
│     IF holiday detected:                │
│       → Use holiday colors              │
│     ELSE:                               │
│       → Use custom time-based colors    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  5. Generate Snake SVG                  │
│     - Uses selected colors              │
│     - Creates light & dark versions     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  6. Commit & Push to output branch      │
└─────────────────────────────────────────┘
```

## 🎨 Supported Holiday Themes

| Holiday | Period | Colors |
|---------|--------|--------|
| 🎃 Halloween | Oct 1 - Nov 1 | Orange & Black |
| 🎄 Christmas | Dec 1 - Dec 31 | Red & Green |
| 🧧 Lunar New Year | Jan 20 - Feb 20 | Red & Gold |
| 🏳️‍🌈 Pride Month | June | Rainbow |
| 🎉 Custom Events | Anytime | Auto-detected |

## 🧪 Testing

### Local Testing

```bash
cd .github/scripts

# Run the detector
python detect_github_holiday_colors.py [username]

# Run the visual test
python test_holiday_detection.py [username]

# Or use the demo script
chmod +x demo.sh
./demo.sh [username]
```

### Expected Output

When a holiday is detected:
```json
{
  "holiday_detected": true,
  "theme_name": "halloween",
  "theme_description": "Halloween Theme (Orange & Black)",
  "light_color": "#FF8C00",
  "dark_color": "#FFA500",
  "light_dots": "#FFE4B5, #FFA500, #FF8C00, #FF6347, #8B4513",
  "dark_dots": "#000000, #8B4513, #FF6347, #FF8C00, #FFA500"
}
```

When no holiday is detected:
```json
{
  "holiday_detected": false
}
```

## 🔧 Customization

### Adding New Holiday Patterns

Edit `detect_github_holiday_colors.py`:

```python
holiday_patterns = {
    'your_holiday': {
        'colors': ['#COLOR1', '#COLOR2', '#COLOR3', '#COLOR4', '#COLOR5'],
        'date_range': (start_month, start_day, end_month, end_day),
        'description': 'Your Holiday Theme Description',
    },
    # ... existing patterns
}
```

### Adjusting Color Selection

The script automatically:
- Sorts colors by brightness
- Selects appropriate colors for light/dark modes
- Ensures proper gradient for contribution levels

You can modify the `generate_color_scheme()` function to customize this behavior.

## 🚀 Deployment

The feature is automatically enabled once the files are committed to the repository. The workflow will:

1. Run automatically every hour (via cron schedule)
2. Run on every push to master branch
3. Can be manually triggered via GitHub Actions UI

## 📊 Benefits

✅ **Automatic** - No manual intervention needed
✅ **Dynamic** - Always uses current GitHub theme
✅ **Fallback** - Maintains existing custom themes when no holiday
✅ **Flexible** - Easy to add new holiday patterns
✅ **Testable** - Comprehensive testing tools included
✅ **Documented** - Full documentation and examples

## 🛠️ Technical Details

- **Language**: Python 3.11+
- **Dependencies**: requests, beautifulsoup4, lxml
- **Web Scraping**: Fetches live GitHub profile pages
- **Color Extraction**: Parses SVG/CSS for contribution colors
- **Pattern Matching**: Date-based and color-based theme detection
- **Integration**: GitHub Actions workflow with proper output handling

## 💡 Future Enhancements

Potential improvements:
- Cache colors to reduce API calls
- Support more regional holidays
- Machine learning for theme detection
- User-configurable theme priorities
- Real-time color preview in PRs

## 📝 Notes

- The script is designed to be resilient - if anything fails, it gracefully falls back to existing custom schemes
- Color detection happens on every workflow run, ensuring the latest GitHub theme is used
- The workflow outputs detailed logs showing which theme was detected/used
- No breaking changes to existing functionality - all existing features remain intact
