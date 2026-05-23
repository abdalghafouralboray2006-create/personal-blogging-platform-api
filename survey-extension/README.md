# AlexU Survey Shortcut - Chrome Extension

# sorry it is slow but the website is so vague and nothing is documented if want change any thing you can always create a new issue and add and change whatever you want.
Auto-fill your university course surveys with customizable ratings.

## Installation

1. **Download the extension folder** (all files in `survey-extension/`)

2. **Open Chrome Extensions page:**
   - Open Chrome
   - Go to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)

3. **Load the extension:**
   - Click "Load unpacked"
   - Select the `survey-extension` folder
   - The extension should now appear in your extensions list

4. **Pin the extension** (optional):
   - Click the puzzle icon in Chrome toolbar
   - Find "AlexU Survey Shortcut"
   - Click the pin icon to keep it visible

## Usage

1. **Open the survey page** on your university website

2. **Click the extension icon** in your Chrome toolbar

3. **Customize your ratings** (optional):
   - 😡 = 20 (Poor)
   - 😐 = 60 (Neutral) - Default
   - 😘 = 100 (Excellent)
   
   Set different ratings for:
   - Materials
   - Professor
   - TA

4. **Click "Finish Survey"** and the extension will automatically:
   - Go through each course
   - Fill in all ratings
   - Save each section
   - Complete the entire survey

## Features

- ✅ Automatic survey completion
- ✅ Customizable ratings per course
- ✅ Remembers your preferences
- ✅ Clean, modern UI
- ✅ Works automatically when clicked




## Troubleshooting

**Extension won't load:**
- Make sure you've selected the folder containing `manifest.json`
- Check that all files are in the same folder

**"Make sure you're on the survey page" error:**
- Ensure you're on the actual survey page before clicking "Finish Survey"
- The page should have a `#slcstuCourses` select element

**Survey doesn't complete:**
- Check browser console (F12) for errors
- Make sure the survey page structure matches the expected format

## Technical Details

- Uses Chrome's Manifest V3
- Stores preferences in `chrome.storage.local`
- Executes script directly in the survey page context
- No external dependencies
