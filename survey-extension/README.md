# AlexU Survey Shortcut - Chrome Extension

**Note:**

# sorry The website is quite vague with no documentation available. If you want to change anything, feel free to [create a new issue](https://github.com/Wael-06/experimental-lab/issues) and suggest improvements.

Auto-fill your university course surveys with customizable ratings.

## Installation

### Step 1: Download
Download the latest release:
- **[Download survey-extension.zip](https://github.com/Wael-06/experimental-lab/releases/download/v1.0.0-survey-extension/survey-extension.zip)**

### Step 2: Extract
Extract the ZIP file to a folder on your computer.

### Step 3: Load in Chrome
1. Open **Chrome** (or any Chromium-based browser like Brave, Edge, or Opera)
2. Go to `chrome://extensions/`
3. Enable **"Developer mode"** (toggle switch in top-right corner)
4. Click **"Load unpacked"**
5. Select the extracted `survey-extension` folder
6. The extension should now appear in your extensions list ✅

## Usage

1. **Open the survey page** on your university website
2. **Click the extension icon** in your Chrome toolbar
3. **Customize your ratings** (optional):
   - 😡 = 20 (Poor)
   - 😐 = 60 (Neutral) - **Default**
   - 😘 = 100 (Excellent)
   
   Set different ratings for:
   -  Materials
   -  Professor
   -  TA

4. **Click "⚡ Start"** and the extension will automatically:
   - Go through each course
   - Fill in all ratings
   - Save each section
   - Handle multiple TAs
   - Complete the entire survey

## ✨ Features

- ✅ Automatic survey completion
- ✅ Customizable ratings per course
- ✅ Remembers your preferences between sessions
- ✅ Dark mode support 🌙
- ✅ Stop button to cancel automation anytime
- ✅ Handles multiple teaching assistants (TAs)
- ✅ Clean, modern UI
- ✅ Works on all Alexandria University survey pages

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Extension won't load** | Make sure you selected the folder containing `manifest.json`. All files must be in the same folder. |
| **"Course selector not found" error** | Ensure you're on the actual survey page. The page must have a `#slcstuCourses` select element. |
| **Survey doesn't complete on first run** | If there are multiple TAs, the page may need time to load. Try running it again or wait a few seconds. |
| **Nothing happens** | Open browser console (F12) to check for errors. Make sure the survey page structure matches the expected format. |

## 📝 Development

### File Structure
