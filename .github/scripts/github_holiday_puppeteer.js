#!/usr/bin/env node

const puppeteer = require('puppeteer');

async function detectGitHubHoliday(username) {
  console.log(`Detecting holiday theme for GitHub user: ${username}`);
  console.log(`Timestamp: ${new Date().toISOString()}`);

  let browser;
  try {
    // Launch the browser
    browser = await puppeteer.launch({
      headless: true,
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu'
      ]
    });

    const page = await browser.newPage();

    // Set viewport and user agent
    await page.setViewport({ width: 1920, height: 1080 });
    await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36');

    const url = `https://github.com/${username}`;
    console.log(`\n=== Method 1: Live DOM color extraction ===`);
    console.log(`Fetching rendered page from ${url}...`);

    // Navigate to the page and wait for it to fully load
    await page.goto(url, {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    // Wait for the contribution graph to load
    await page.waitForSelector('.ContributionCalendar-day', {
      timeout: 10000
    });

    // Extract the actual rendered colors
    const colorData = await page.evaluate(() => {
      const days = document.querySelectorAll('.ContributionCalendar-day');
      const levelColors = {};

      days.forEach(day => {
        const level = day.getAttribute('data-level');
        if (level && !levelColors[level]) {
          // Get computed style
          const computedStyle = window.getComputedStyle(day);
          let color = computedStyle.fill || computedStyle.backgroundColor;

          // Convert to hexadecimal
          if (color && color.startsWith('rgb')) {
            const rgb = color.match(/\d+/g);
            if (rgb && rgb.length >= 3) {
              color = '#' + rgb.slice(0, 3).map(x =>
                parseInt(x).toString(16).padStart(2, '0')
              ).join('');
            }
          }

          if (color && color !== '#000000' && color !== 'rgb(0, 0, 0)') {
            levelColors[level] = color.toLowerCase();
          }
        }
      });

      return levelColors;
    });

    console.log(`✓ Extracted ${Object.keys(colorData).length} color levels from live DOM`);
    console.log(`  Colors:`, colorData);

    // Analyze colors to detect holiday themes
    if (Object.keys(colorData).length >= 3) {
      const theme = analyzeColorsForTheme(colorData);
      if (theme) {
        console.log(`✓ Detected ${theme} theme from live colors`);
        return createResult(theme, 'dom-colors', colorData);
      }
    }

    // Extract the holiday theme and corresponding CSS color palette for contribution blocks
    const holidayData = await page.evaluate(() => {
      // Find the element with the data-holiday attribute
      const holidayElement = document.querySelector('[data-holiday]');
      if (!holidayElement) return null;

      // Get the value of the data-holiday attribute
      const holidayName = holidayElement.getAttribute('data-holiday');

      // Construct CSS variable names based on the holiday name
      const cssVariableNames = [
        `--contribution-default-bgColor-0`, // Fixed default background color
        `--contribution-${holidayName}-bgColor-1`,
        `--contribution-${holidayName}-bgColor-2`,
        `--contribution-${holidayName}-bgColor-3`,
        `--contribution-${holidayName}-bgColor-4`
      ];

      // Retrieve the corresponding CSS variable values
      const root = document.documentElement;
      const colors = cssVariableNames.map(name => ({
        name,
        color: getComputedStyle(root).getPropertyValue(name).trim()
      }));

      return { holidayName, colors };
    });

    if (holidayData) {
      console.log(`Detected holiday: ${holidayData.holidayName}`);
      console.log(`CSS Variables and Colors:`);
      holidayData.colors.forEach(({ name, color }) => {
        console.log(`${name}: ${color}`);
      });
      return createResult(holidayData.holidayName, 'css-variable', {
        [holidayData.holidayName]: holidayData.colors
      });
    } else {
      console.log('No holiday detected.');
    }

    // Fallback to date-based detection
    console.log(`\n=== Method 3: Date-based holiday detection ===`);
    const dateTheme = checkHolidayByDate();
    if (dateTheme) {
      console.log(`✓ Current date matches ${dateTheme} period`);
      return createResult(dateTheme, 'date');
    }

    // Default theme
    console.log('\n✗ No holiday theme detected');
    return createResult('default', 'none');

  } catch (error) {
    console.error(`Puppeteer extraction failed: ${error.message}`);
    // Fallback to date detection
    console.log('\n=== Fallback: Date-based detection ===');
    const dateTheme = checkHolidayByDate();
    if (dateTheme) {
      console.log(`✓ Date fallback: ${dateTheme}`);
      return createResult(dateTheme, 'date-fallback');
    }
    return createResult('default', 'error');
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

function analyzeColorsForTheme(colors) {
  const colorValues = Object.values(colors).join(' ').toLowerCase();

  // Halloween: Orange theme
  if (colorValues.includes('fb85') || colorValues.includes('d471') ||
      colorValues.includes('bc4c') || colorValues.includes('f60')) {
    return 'halloween';
  }

  // Christmas: Red and green mix
  const hasRed = colorValues.includes('cf22') || colorValues.includes('a40e');
  const hasGreen = colorValues.includes('1a7f') || colorValues.includes('1163');
  if (hasRed && hasGreen) {
    return 'christmas';
  }

  // Pink and purple theme
  const hasPink = colorValues.includes('bf39') || colorValues.includes('8250');
  const hasPurple = colorValues.includes('622c') || colorValues.includes('bf3');
  if (hasPink || hasPurple) {
    const month = new Date().getMonth() + 1;
    if (month === 2) return 'valentines';
    if (month === 1 || month === 2) return 'lunar_new_year';
    if (month === 6) return 'pride';
  }

  return null;
}

function checkHolidayByDate() {
  const now = new Date();
  const month = now.getMonth() + 1;
  const day = now.getDate();

  const holidays = {
    halloween: { start: [10, 25], end: [11, 1] },
    christmas: { start: [12, 1], end: [12, 31] },
    lunar_new_year: { start: [1, 20], end: [2, 20] },
    valentines: { start: [2, 10], end: [2, 14] },
    pride: { start: [6, 1], end: [6, 30] }
  };

  for (const [holiday, range] of Object.entries(holidays)) {
    const [startM, startD] = range.start;
    const [endM, endD] = range.end;

    if (month === startM && day >= startD ||
        month === endM && day <= endD ||
        (month > startM && month < endM)) {
      return holiday;
    }
  }
  return null;
}

function createResult(theme, method, extractedColors = null) {
  const themes = {
    halloween: {
      light_color: '#fb8500',
      dark_color: '#d47100',
      light_dots: '#fb8500, #d47100, #bc4c00, #953800, #762d0a',
      dark_dots: '#d47100, #bc4c00, #953800, #762d0a, #5a1e02',
      description: 'Halloween Theme (Orange)'
    },
    christmas: {
      light_color: '#1a7f37',
      dark_color: '#cf222e',
      light_dots: '#1a7f37, #116329, #0969da, #0550ae, #cf222e',
      dark_dots: '#116329, #0550ae, #0969da, #8250df, #a40e26',
      description: 'Christmas Theme (Green & Red)'
    },
    lunar_new_year: {
      light_color: '#bf3989',
      dark_color: '#cf222e',
      light_dots: '#bf3989, #8250df, #cf222e, #a40e26, #82071e',
      dark_dots: '#8250df, #a40e26, #82071e, #6e011a, #540719',
      description: 'Lunar New Year (Pink & Red)'
    },
    valentines: {
      light_color: '#bf3989',
      dark_color: '#8250df',
      light_dots: '#bf3989, #8250df, #cf222e, #fb8500, #a40e26',
      dark_dots: '#8250df, #a40e26, #82071e, #6e011a, #622cbc',
      description: 'Valentine\'s Day (Pink & Purple)'
    },
    pride: {
      light_color: '#0969da',
      dark_color: '#8250df',
      light_dots: '#cf222e, #fb8500, #d4a72c, #1a7f37, #0969da',
      dark_dots: '#a40e26, #d47100, #9a6700, #116329, #622cbc',
      description: 'Pride Month (Rainbow)'
    },
    default: {
      light_color: '#9BE9A8',
      dark_color: '#40C463',
      light_dots: '#9BE9A8, #40C463, #30A14E, #216E39',
      dark_dots: '#0E4429, #006D32, #26A641, #39D353',
      description: 'Default GitHub Green'
    }
  };

  const themeData = themes[theme] || themes.default;

  return {
    holiday_detected: theme !== 'default',
    theme_name: theme,
    theme_description: themeData.description,
    light_color: themeData.light_color,
    dark_color: themeData.dark_color,
    light_dots: themeData.light_dots,
    dark_dots: themeData.dark_dots,
    detection_method: method,
    ...(extractedColors && { extracted_colors: JSON.stringify(extractedColors) })
  };
}

// Main function
async function main() {
  const username = process.env.GITHUB_USERNAME || process.argv[2] || 'diverger';
  const result = await detectGitHubHoliday(username);

  // Output in GitHub Actions format
  const githubOutput = process.env.GITHUB_OUTPUT;
  if (githubOutput) {
    const fs = require('fs');
    let output = '';
    for (const [key, value] of Object.entries(result)) {
      const val = typeof value === 'boolean' ? (value ? 'true' : 'false') : value;
      output += `${key}=${val}\n`;
    }
    fs.appendFileSync(githubOutput, output);
  }

  // Also print JSON
  console.log('\n=== Detection Result ===');
  console.log(JSON.stringify(result, null, 2));
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { detectGitHubHoliday };