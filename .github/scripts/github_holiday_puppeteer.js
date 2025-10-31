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
    console.log(`\n=== Method 1: CSS Variable Detection ===`);
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

    // Extract the holiday theme and corresponding CSS color palette for contribution grid
    const holidayData = await page.evaluate(() => {
      // Find the element with the data-holiday attribute
      const holidayElement = document.querySelector('[data-holiday]');

      // Get the value of the data-holiday attribute (or null if no holiday)
      const holidayName = holidayElement ? holidayElement.getAttribute('data-holiday') : null;

      // Construct CSS variable names for grid colors
      const cssVariableNames = [
        `--contribution-default-bgColor-0`, // Fixed default background color (level 0)
        `--contribution-${holidayName || 'default'}-bgColor-1`,
        `--contribution-${holidayName || 'default'}-bgColor-2`,
        `--contribution-${holidayName || 'default'}-bgColor-3`,
        `--contribution-${holidayName || 'default'}-bgColor-4`
      ];

      // Helper function to get CSS variable value for a specific color scheme
      const getColorsForScheme = (scheme) => {
        // Create a temporary element to test media query
        const testDiv = document.createElement('div');
        testDiv.style.colorScheme = scheme; // Set color-scheme to 'light' or 'dark'
        document.body.appendChild(testDiv);

        const colors = cssVariableNames.map((name, index) => {
          const color = getComputedStyle(testDiv).getPropertyValue(name).trim();
          return {
            level: index,
            variable: name,
            color: color || null
          };
        });

        document.body.removeChild(testDiv);
        return colors;
      };

      // Get colors for both light and dark schemes
      // Note: We need to extract from the root with the current scheme
      const root = document.documentElement;

      // For light theme
      const lightColors = cssVariableNames.map((name, index) => {
        // Try to get the light theme value
        // GitHub's CSS uses media queries, so we extract from current computed style
        const color = getComputedStyle(root).getPropertyValue(name).trim();
        return {
          level: index,
          variable: name,
          color: color || null
        };
      });

      // For dark theme, we need to emulate dark mode
      // Set the data-color-mode attribute to force dark mode
      const originalColorMode = root.getAttribute('data-color-mode');
      const originalLightTheme = root.getAttribute('data-light-theme');
      const originalDarkTheme = root.getAttribute('data-dark-theme');

      root.setAttribute('data-color-mode', 'dark');
      root.setAttribute('data-dark-theme', 'dark');

      const darkColors = cssVariableNames.map((name, index) => {
        const color = getComputedStyle(root).getPropertyValue(name).trim();
        return {
          level: index,
          variable: name,
          color: color || null
        };
      });

      // Restore original attributes
      if (originalColorMode) {
        root.setAttribute('data-color-mode', originalColorMode);
      } else {
        root.removeAttribute('data-color-mode');
      }
      if (originalLightTheme) {
        root.setAttribute('data-light-theme', originalLightTheme);
      }
      if (originalDarkTheme) {
        root.setAttribute('data-dark-theme', originalDarkTheme);
      }

      return { holidayName, lightColors, darkColors };
    });

    if (holidayData && holidayData.holidayName) {
      console.log(`✓ Detected holiday: ${holidayData.holidayName}`);
      console.log(`  Light theme grid colors:`);
      holidayData.lightColors.forEach(({ level, variable, color }) => {
        console.log(`    Level ${level}: ${color} (${variable})`);
      });
      console.log(`  Dark theme grid colors:`);
      holidayData.darkColors.forEach(({ level, variable, color }) => {
        console.log(`    Level ${level}: ${color} (${variable})`);
      });
      return createResult(holidayData.holidayName, 'css-variable', holidayData.lightColors, holidayData.darkColors);
    } else {
      console.log('✗ No holiday attribute found, using default colors');
      console.log(`  Light theme grid colors:`);
      holidayData.lightColors.forEach(({ level, variable, color }) => {
        console.log(`    Level ${level}: ${color} (${variable})`);
      });
      console.log(`  Dark theme grid colors:`);
      holidayData.darkColors.forEach(({ level, variable, color }) => {
        console.log(`    Level ${level}: ${color} (${variable})`);
      });
      return createResult('default', 'css-variable', holidayData.lightColors, holidayData.darkColors);
    }    // Fallback to date-based detection
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

function createResult(theme, method, lightGridColors = null, darkGridColors = null) {
  // Build the result object
  const result = {
    holiday_detected: theme !== 'default',
    theme_name: theme,
    detection_method: method
  };

  // If grid colors were extracted, include them in the result
  if (lightGridColors && Array.isArray(lightGridColors)) {
    result.light_grid_colors = lightGridColors.map(({ level, color }) => ({
      level,
      color
    }));

    // Provide a simple palette format for light theme
    const lightColorList = lightGridColors.map(({ color }) => color).filter(c => c).join(', ');
    result.light_color_palette = lightColorList;
  }

  if (darkGridColors && Array.isArray(darkGridColors)) {
    result.dark_grid_colors = darkGridColors.map(({ level, color }) => ({
      level,
      color
    }));

    // Provide a simple palette format for dark theme
    const darkColorList = darkGridColors.map(({ color }) => color).filter(c => c).join(', ');
    result.dark_color_palette = darkColorList;
  }

  return result;
}// Main function
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