const subjects = [
    "Probability & Statistics",
    "Data Structure-I",
    "Electronic Circuit Analysis",
    "Digital Logic Circuits-II",
    "Signals and Systems",
    "Control Systems",
    "Analysis of Electrical Circuits",
    "Issues of Energy"
];

let currentSubjects = [...defaultSubjects];

const scoreMap = {
    "😡": 20,
    "😐": 60,
    "😘": 100
};

const emojis = ["😡", "😐", "😘"];

// Dark mode handling
async function loadTheme() {
    const result = await chrome.storage.local.get('theme');
    return result.theme || 'light';
}

async function saveTheme(theme) {
    await chrome.storage.local.set({ theme });
}

async function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const icon = document.querySelector('#themeToggle .icon');
    icon.textContent = theme === 'dark' ? '☀️' : '🌙';
}

// Theme toggle handler
document.getElementById('themeToggle').addEventListener('click', async () => {
    const currentTheme = await loadTheme();
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    await saveTheme(newTheme);
    await applyTheme(newTheme);
});

// Load saved settings or use defaults
async function loadSettings() {
    const result = await chrome.storage.local.get('surveySettings');
    return result.surveySettings || {};
}

// Save settings
async function saveSettings(settings) {
    await chrome.storage.local.set({ surveySettings: settings });
}

async function fetchPageSubjects() {
    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (!tab || !tab.id) return [];

        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => {
                const selects = [...document.querySelectorAll('select')].filter(select => select.options.length > 1);
                const courseSelect = selects.find(select => /course|class|subject|slcstuCourses/i.test(select.id + ' ' + select.name));
                const target = courseSelect || selects[0];
                if (!target) return [];
                return [...new Set([...target.options].map(option => option.text.trim()).filter(Boolean))];
            }
        });

        if (!results || !results[0] || !Array.isArray(results[0].result)) return [];
        return results[0].result;
    } catch (error) {
        console.warn('Could not fetch page subjects:', error);
        return [];
    }
}

// Create course cards
async function renderCourses() {
    const container = document.getElementById('courses');
    const savedSettings = await loadSettings();

    const pageSubjects = await fetchPageSubjects();
    if (pageSubjects.length) {
        currentSubjects = pageSubjects;
    }

    container.innerHTML = '';

    currentSubjects.forEach(subject => {
        const defaults = savedSettings[subject] || {
            materials: 60,
            prof: 60,
            ta: 60
        };

        const card = document.createElement('div');
        card.className = 'course-card';
        card.innerHTML = `
            <div class="course-name">${subject}</div>
            <div class="rating-grid">
                <span class="rating-label">Materials:</span>
                <div class="rating-buttons materials-btns" data-course="${subject}" data-type="materials">
                    ${emojis.map(emoji => `
                        <button class="rating-btn ${scoreMap[emoji] === defaults.materials ? 'active' : ''}" data-score="${scoreMap[emoji]}">${emoji}</button>
                    `).join('')}
                </div>
                <span class="rating-label">Professor:</span>
                <div class="rating-buttons prof-btns" data-course="${subject}" data-type="prof">
                    ${emojis.map(emoji => `
                        <button class="rating-btn ${scoreMap[emoji] === defaults.prof ? 'active' : ''}" data-score="${scoreMap[emoji]}">${emoji}</button>
                    `).join('')}
                </div>
                <span class="rating-label">TA:</span>
                <div class="rating-buttons ta-btns" data-course="${subject}" data-type="ta">
                    ${emojis.map(emoji => `
                        <button class="rating-btn ${scoreMap[emoji] === defaults.ta ? 'active' : ''}" data-score="${scoreMap[emoji]}">${emoji}</button>
                    `).join('')}
                </div>
            </div>
        `;
        container.appendChild(card);
    });

    document.querySelectorAll('.rating-buttons').forEach(group => {
        group.querySelectorAll('.rating-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                group.querySelectorAll('.rating-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                await updateSettings();
            });
        });
    });
}

// Update settings in storage
async function updateSettings() {
    const settings = {};

    currentSubjects.forEach(subject => {
        settings[subject] = {
            materials: getActiveScore(subject, 'materials'),
            prof: getActiveScore(subject, 'prof'),
            ta: getActiveScore(subject, 'ta')
        };
    });

    await saveSettings(settings);
}

// Get active score for a course and type
function getActiveScore(course, type) {
    const group = document.querySelector(`.${type}-btns[data-course="${course}"]`);
    if (!group) return 60;
    const activeBtn = group.querySelector('.rating-btn.active');
    return activeBtn ? parseInt(activeBtn.dataset.score, 10) : 60;
}

// Show status message
function showStatus(message, type = 'success') {
    const status = document.getElementById('status');
    status.textContent = message;
    status.className = 'status';
    if (type === 'error') status.classList.add('error');
    if (type === 'processing') status.classList.add('processing');
    status.style.display = 'block';

    if (type !== 'processing') {
        setTimeout(() => {
            status.style.display = 'none';
        }, 3000);
    }
}

// Global stop flag shared with injected script
window.SURVEY_STOP_FLAG = false;
let surveyRunning = false;

// Finish button handler
document.getElementById('finishBtnTop').addEventListener('click', async () => {
    const btn = document.getElementById('finishBtnTop');
    const stopBtn = document.getElementById('stopBtnTop');
    
    if (surveyRunning) return;
    surveyRunning = true;
    window.SURVEY_STOP_FLAG = false;
    
    btn.disabled = true;
    btn.innerHTML = '⚡ Running...';
    stopBtn.style.display = 'block';
    
    showStatus('Starting smart survey fill...', 'processing');

    try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const settings = await loadSettings();

        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: executeSurveyFast,
            args: [settings]
        });

        const completed = results?.[0]?.result?.completed;
        const message = results?.[0]?.result?.message || 'Survey automation finished.';

        if (completed) {
            showStatus(`✓ ${message}`, 'success');
        } else {
            showStatus(`⚠ ${message}`, 'error');
        }
    } catch (error) {
        console.error(error);
        showStatus('⚠ Error: Make sure you\'re on the survey page and try again.', 'error');
    } finally {
        surveyRunning = false;
        window.SURVEY_STOP_FLAG = false;
        btn.innerHTML = '⚡ Start';
        btn.disabled = false;
        stopBtn.style.display = 'none';
    }
});

// Stop button handler
document.getElementById('stopBtnTop').addEventListener('click', () => {
    window.SURVEY_STOP_FLAG = true;
    showStatus('Stopping survey automation...', 'error');
    document.getElementById('finishBtnTop').innerHTML = '⚡ Start';
    document.getElementById('finishBtnTop').disabled = false;
    setTimeout(() => {
        document.getElementById('stopBtnTop').style.display = 'none';
    }, 500);
});

// ULTRA FAST & SMART Survey execution function (injected into page)
async function executeSurveyFast(customSettings) {
    const DEFAULT_SCORE = 60;
    const wait = (ms) => new Promise(r => setTimeout(r, ms));

    function getCourseSelect() {
        return document.querySelector('#slcstuCourses');
    }

    function getTabButtons() {
        const evalDiv = document.querySelector('#tabs');
        if (!evalDiv) return [];
        return [...evalDiv.querySelectorAll('button.tablinks')];
    }

    function isTabFilled() {
        const radios = [...document.querySelectorAll('#EvaluationDiv input[type="radio"]:not([disabled])')].filter(r => r.offsetParent !== null);
        return radios.length > 0 && radios.some(r => r.checked);
    }

    function findSaveButton() {
        const evalDiv = document.querySelector('#EvaluationDiv');
        if (!evalDiv) return null;
        const buttons = [...evalDiv.querySelectorAll('button, input[type="button"], input[type="submit"]')];
        return buttons.find(el => /save|submit/i.test((el.innerText || el.value || '').trim()));
    }

    function getRadioGroups() {
        const radios = [...document.querySelectorAll('#EvaluationDiv input[type="radio"]:not([disabled])')].filter(r => r.offsetParent !== null);
        const groups = new Map();
        radios.forEach(radio => {
            if (!radio.name) return;
            const list = groups.get(radio.name) || [];
            list.push(radio);
            groups.set(radio.name, list);
        });
        return [...groups.values()];
    }

    function pickRadioForGroup(radios, score) {
        const exact = radios.find(radio => String(radio.value) === String(score) || String(radio.dataset.score) === String(score));
        if (exact) return exact;
        if (radios.length === 3) {
            if (score >= 100) return radios[2];
            if (score <= 20) return radios[0];
            return radios[1];
        }
        if (score >= 100) return radios[radios.length - 1];
        if (score <= 20) return radios[0];
        return radios[Math.floor((radios.length - 1) / 2)];
    }

    function getUnfilledRadios() {
        const groups = getRadioGroups();
        return groups.filter(radios => !radios.some(r => r.checked));
    }

    // 🆕 Wait until at least one unfilled radio group appears (max 5 seconds)
    async function waitForUnfilledRadios(maxWait = 5000) {
        const start = Date.now();
        while (Date.now() - start < maxWait) {
            const unfilled = getUnfilledRadios();
            if (unfilled.length > 0) return true;
            await wait(200);
        }
        return false;   // timeout – the page may not have loaded any questions
    }

    function fillVisibleRadios(score) {
        const groups = getRadioGroups();
        groups.forEach(radios => {
            const selected = pickRadioForGroup(radios, score);
            if (selected && !selected.checked) {
                selected.checked = true;
                selected.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    }

    function click(el) {
        if (!el) return;
        el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
    }

    async function clickAllConfirms() {
        let confirm1 = document.querySelector('#dailogAgree');
        if (confirm1) {
            click(confirm1);
            await wait(100);
        }
        let confirm2 = document.querySelector('#popup_ok');
        if (confirm2) {
            click(confirm2);
            await wait(150);
        }
    }

    async function saveCurrentSection() {
        const saveBtn = findSaveButton();
        if (saveBtn) {
            click(saveBtn);
            await clickAllConfirms();
        }
    }

    async function clickTab(tabButtons, index) {
        if (tabButtons.length && tabButtons[index]) {
            click(tabButtons[index]);
            await wait(250);
            return true;
        }
        return false;
    }

    const courseSelect = getCourseSelect();
    if (!courseSelect) {
        return { completed: false, message: 'Course selector (#slcstuCourses) not found' };
    }

    const courses = [...courseSelect.options].filter(option => option.value !== '' && option.text.trim());
    if (!courses.length) {
        return { completed: false, message: 'No courses found in selector' };
    }

    const startTime = Date.now();
    console.log(`🚀 Starting survey fill for ${courses.length} course(s)...`);

    for (let i = 0; i < courses.length; i++) {
        if (window.SURVEY_STOP_FLAG) {
            console.log('⛔ Survey stopped by user');
            break;
        }

        courseSelect.selectedIndex = i;
        courseSelect.dispatchEvent(new Event('change', { bubbles: true }));
        await wait(1200);

        const courseName = courses[i].text.trim();
        const settings = customSettings[courseName] || {
            materials: DEFAULT_SCORE,
            prof: DEFAULT_SCORE,
            ta: DEFAULT_SCORE
        };

        console.log(`📝 [${i + 1}/${courses.length}] ${courseName}`);

        const tabButtons = getTabButtons();
        if (!tabButtons.length) {
            fillVisibleRadios(settings.materials);
            await saveCurrentSection();
            console.log(`✅ Completed: ${courseName}`);
            continue;
        }

        for (let tabIdx = 0; tabIdx < tabButtons.length; tabIdx++) {
            if (window.SURVEY_STOP_FLAG) break;

            await clickTab(tabButtons, tabIdx);
            await wait(300);

            const tabLabel = (tabButtons[tabIdx].innerText || '').toLowerCase();
            let score = settings.materials;
            if (/professor|prof|instructor|teacher/i.test(tabLabel)) score = settings.prof;
            else if (/ta|assistant/i.test(tabLabel)) score = settings.ta;

            const staffSelects = [...document.querySelectorAll('#EvaluationDiv select')]
                .filter(s => s.offsetParent !== null && /(slcStaff|staff|instructor|assistant)/i.test((s.id || '') + ' ' + (s.name || '')));

            let totalItems = 0;

            if (staffSelects.length) {
                for (const select of staffSelects) {
                    const startIdx = (select.options[0] && select.options[0].value) ? 0 : 1;
                    for (let staffIdx = startIdx; staffIdx < select.options.length; staffIdx++) {
                        if (window.SURVEY_STOP_FLAG) break;

                        select.selectedIndex = staffIdx;
                        select.dispatchEvent(new Event('change', { bubbles: true }));

                        // 🔁 Wait until the new staff's radio buttons are ready
                        const ready = await waitForUnfilledRadios(5000);
                        if (!ready) {
                            console.warn(`⚠ No unfilled radios appeared for staff index ${staffIdx} after 5s, skipping.`);
                            continue;   // go to next staff option
                        }

                        let fillCount = 0;
                        while (getUnfilledRadios().length > 0 && fillCount < 50) {
                            if (window.SURVEY_STOP_FLAG) break;

                            console.log(`📊 Filling tab ${tabIdx + 1}/${tabButtons.length} (staff ${staffIdx - startIdx + 1}) item ${fillCount + 1}...`);
                            fillVisibleRadios(score);
                            await saveCurrentSection();
                            await wait(150);
                            fillCount++;
                        }
                        totalItems += Math.max(1, fillCount);
                    }
                    if (window.SURVEY_STOP_FLAG) break;
                }
            } else {
                // No staff selects – wait for radios to appear before filling
                const ready = await waitForUnfilledRadios(5000);
                if (ready) {
                    let fillCount = 0;
                    while (getUnfilledRadios().length > 0 && fillCount < 50) {
                        if (window.SURVEY_STOP_FLAG) break;

                        console.log(`📊 Filling tab ${tabIdx + 1}/${tabButtons.length} (item ${fillCount + 1})...`);
                        fillVisibleRadios(score);
                        await saveCurrentSection();
                        await wait(150);
                        fillCount++;
                    }
                    totalItems = fillCount;
                }
            }

            console.log(`✅ Tab ${tabIdx + 1}/${tabButtons.length} completed (${totalItems} item${totalItems !== 1 ? 's' : ''})`);
        }

        console.log(`✅ Completed: ${courseName}`);
    }

    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    console.log(`🎉 Survey fill completed in ${elapsed}s!`);
    return { completed: true, message: `Survey completed in ${elapsed}s` };
}

(async () => {
    await renderCourses();
    const theme = await loadTheme();
    await applyTheme(theme);
})();
