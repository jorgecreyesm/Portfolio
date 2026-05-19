const SERVER = 'http://localhost:5050';

function parseJobTitle(pageTitle) {
  let t = pageTitle
    // LinkedIn: "Title at Company | LinkedIn"
    .replace(/\s+at\s+.+$/i, '')
    // Strip site suffixes after | or —
    .replace(/\s*[|–—]\s*(LinkedIn|Indeed|Glassdoor|ZipRecruiter|Monster|CalCareers|Workday|Handshake|Greenhouse|Lever|Jobvite|Taleo).*$/i, '')
    // Generic: strip everything after |
    .replace(/\s*\|.*$/, '')
    // CalCareers: "Title - CalCareers"
    .replace(/\s*-\s*CalCareers.*$/i, '')
    .trim();
  return t || pageTitle;
}

async function loadResumes() {
  const select = document.getElementById('resume');
  try {
    const res = await fetch(`${SERVER}/resumes`);
    const data = await res.json();
    select.innerHTML = '<option value="">— select resume —</option>';
    data.resumes.forEach(r => {
      const opt = document.createElement('option');
      opt.value = r;
      opt.textContent = r;
      select.appendChild(opt);
    });
  } catch {
    select.innerHTML = '<option value="">⚠ Server offline</option>';
  }
}

async function init() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab) {
    document.getElementById('urlPreview').textContent = tab.url;
    document.getElementById('jobTitle').value = parseJobTitle(tab.title || '');
  }
  await loadResumes();
}

document.getElementById('logBtn').addEventListener('click', async () => {
  const btn    = document.getElementById('logBtn');
  const status = document.getElementById('status');
  const [tab]  = await chrome.tabs.query({ active: true, currentWindow: true });

  const payload = {
    job_title: document.getElementById('jobTitle').value.trim(),
    pay:       document.getElementById('pay').value.trim(),
    resume:    document.getElementById('resume').value,
    follow_up: document.getElementById('followUp').value.trim(),
    url:       tab?.url || ''
  };

  if (!payload.job_title) {
    status.className = 'error';
    status.textContent = 'Job title is required.';
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Logging…';
  status.textContent = '';

  try {
    const res = await fetch(`${SERVER}/log`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      status.className = 'success';
      status.textContent = '✓ Logged!';
      btn.textContent = '✓ Done';
      setTimeout(() => window.close(), 1200);
    } else {
      throw new Error('server error');
    }
  } catch {
    status.className = 'error';
    status.textContent = '✗ Server not reachable. Run setup.sh first.';
    btn.disabled = false;
    btn.textContent = 'Log Application';
  }
});

init();
