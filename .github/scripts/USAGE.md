# Usage Guide - GitHub Holiday Color Detection

## 🚀 Quick Start

The holiday color detection is **automatically enabled** and runs with your existing snake animation workflow. No configuration needed!

## 🎯 How to Use

### Automatic Mode (Default)

The workflow automatically runs:
- ⏰ Every hour (via cron schedule)
- 📝 On every push to master branch
- 🔘 Manual trigger via GitHub Actions

Simply commit the new files and the feature is active!

### Manual Trigger

1. Go to your repository on GitHub
2. Click on **Actions** tab
3. Select **generate animation** workflow
4. Click **Run workflow** button
5. (Optional) Select color change mode
6. Click **Run workflow**

## 🧪 Testing Locally

### Method 1: Quick Test

```bash
cd .github/scripts
chmod +x demo.sh
./demo.sh diverger
```

Replace `diverger` with any GitHub username.

### Method 2: Python Script

```bash
cd .github/scripts

# Install dependencies
pip install -r requirements.txt

# Run detector
python detect_github_holiday_colors.py diverger

# Check output
cat holiday_colors.json
```

### Method 3: Visual Test (Recommended)

```bash
cd .github/scripts
python test_holiday_detection.py diverger
```

This will show:
- ✅ Detected colors with visual boxes
- 🎨 Generated light/dark themes
- 📊 JSON output

## 🎨 Understanding the Output

### When Holiday is Detected

```
🔍 Testing GitHub Holiday Color Detection for: diverger

=== Detection Result ===
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

The snake animation will use these holiday colors!

### When No Holiday is Detected

```
{
  "holiday_detected": false
}
```

The snake animation falls back to your custom color schemes (hour-based or day-based).

## 📅 Holiday Schedule

| Holiday | Active Period | Theme Colors |
|---------|--------------|--------------|
| 🎃 Halloween | October 1 - November 1 | Orange & Black |
| 🎄 Christmas | December 1 - 31 | Red & Green |
| 🧧 Lunar New Year | ~January 20 - February 20 | Red & Gold |
| 🏳️‍🌈 Pride Month | June 1 - 30 | Rainbow |

*Note: GitHub may add or change holiday themes at any time. The detector will automatically catch new themes!*

## 🔧 Customization

### Add Your Own Holiday Pattern

Edit `.github/scripts/detect_github_holiday_colors.py`:

```python
holiday_patterns = {
    'valentines': {
        'colors': ['#FF1493', '#FF69B4', '#FFB6C1', '#FFC0CB'],
        'date_range': (2, 1, 2, 14),  # Feb 1 - Feb 14
        'description': 'Valentine\'s Day Theme (Pink & Red)',
    },
    # ... other patterns
}
```

### Disable Holiday Detection

If you prefer to always use custom colors, you can disable the holiday detection by modifying `.github/workflows/snake.yml`:

Find this line:
```yaml
HOLIDAY_DETECTED: ${{ steps.holiday.outputs.holiday_detected }}
```

Change to:
```yaml
HOLIDAY_DETECTED: false
```

Or simply remove the "Detect GitHub Holiday Colors" step.

## 🐛 Troubleshooting

### Colors Not Updating

**Problem**: Snake animation still shows old colors after a holiday started.

**Solutions**:
1. Wait for the next hourly cron run
2. Manually trigger the workflow from GitHub Actions
3. Check workflow logs for errors

### Holiday Not Detected

**Problem**: It's a holiday period but detection shows `false`.

**Possible Causes**:
1. GitHub hasn't activated the holiday theme yet
2. Date range in code doesn't match current date
3. Color pattern doesn't match (GitHub changed their theme)

**Debug**:
```bash
# Run test locally to see what colors are detected
python test_holiday_detection.py diverger

# Check the all_colors array - do they look special?
```

### Script Errors

**Problem**: Workflow fails with Python errors.

**Solutions**:
1. Check dependencies are installed correctly
2. Verify Python 3.11+ is being used
3. Check network access to GitHub.com
4. Review workflow logs for specific error messages

### No Colors Detected

**Problem**: Script returns empty colors array.

**Possible Causes**:
1. Network issue fetching GitHub profile
2. GitHub changed their HTML structure
3. User profile is private or doesn't exist

**Fix**: Update the color extraction logic in `extract_contribution_colors()` function.

## 💡 Pro Tips

### Preview Before Commit

Test locally before committing changes:

```bash
# Make your changes to the script
vim detect_github_holiday_colors.py

# Test immediately
python test_holiday_detection.py diverger

# Check it works as expected
```

### Check Workflow Logs

To see what theme was used:

1. Go to **Actions** tab
2. Click on latest workflow run
3. Expand **Set color scheme** step
4. Look for lines like:
   ```
   🎉 Using detected holiday theme!
   Theme: Halloween Theme (Orange & Black) (halloween)
   ```

### Force Specific Colors

You can manually set colors by using the workflow's manual trigger with the `manual` mode and selecting a specific style.

## 📊 Workflow Visualization

```
User Activity → Contribution Graph
                      ↓
              GitHub Profile Page
                      ↓
              [Color Detector] ← Runs every hour
                      ↓
                  ┌───┴────┐
                  ↓        ↓
          Holiday Theme   No Holiday
          Detected        Detected
                  ↓        ↓
          Holiday Colors  Custom Colors
                  ↓        ↓
                  └───┬────┘
                      ↓
              Snake Animation SVG
                      ↓
              Committed to repo
```

## 🔗 Related Files

- 📄 **README.md** - Main documentation
- 📄 **IMPLEMENTATION.md** - Technical details
- 🐍 **detect_github_holiday_colors.py** - Main detector script
- 🧪 **test_holiday_detection.py** - Visual test tool
- ⚙️ **snake.yml** - GitHub Actions workflow
- 📦 **requirements.txt** - Python dependencies

## 🆘 Getting Help

If you encounter issues:

1. ✅ Check this usage guide
2. 📖 Read the IMPLEMENTATION.md for technical details
3. 🔍 Search existing GitHub Issues
4. 🐛 Create a new issue with:
   - Error messages
   - Workflow logs
   - Local test output
   - Expected vs actual behavior

## 🎉 Enjoy!

Your snake animation will now automatically celebrate GitHub holidays with you! 🐍✨
