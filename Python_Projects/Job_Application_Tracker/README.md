# Job Application Tracker

A Chrome extension + local Python server that lets you log job applications to your Excel spreadsheet in one click — directly from any job posting page.

---

## How It Works

1. You browse to a job posting in Chrome
2. Click the extension icon in your toolbar
3. The popup pre-fills the job title from the page
4. You fill in pay range, pick your resume, add any notes
5. Click **Log Application** — a new row is added to your Excel file instantly

No copy-pasting, no tab-switching.

---

## Project Structure

```
Job_Application_Tracker/
├── server.py           # Flask server — handles Excel writes and resume list
├── setup.sh            # One-time install script
├── requirements.txt    # Python dependencies
└── extension/
    ├── manifest.json   # Chrome extension config (Manifest V3)
    ├── popup.html      # Extension popup UI
    ├── popup.js        # Popup logic — parses page title, calls server
    └── icons/          # Extension icons
```

---

## Setup

### 1. Run the setup script (one time only)

```bash
bash setup.sh
```

This will:
- Install Python dependencies (`flask`, `flask-cors`, `openpyxl`)
- Register a macOS LaunchAgent so the server starts automatically on login
- Start the server immediately on `http://localhost:5050`

### 2. Load the extension in Chrome

1. Open Chrome and go to `chrome://extensions`
2. Enable **Developer mode** (toggle in the top right)
3. Click **Load unpacked**
4. Select the `extension/` folder inside this project

The extension icon will appear in your Chrome toolbar.

---

## Usage

| Field | Description |
|---|---|
| Job Title | Auto-filled from the page title — edit as needed |
| Pay Range | Enter the salary range from the posting |
| Resume Used | Dropdown pulled live from your Resume Versions folder |
| Follow Up / Notes | Optional — referral name, deadline, recruiter contact, etc. |

Works on LinkedIn, Indeed, CalCareers, Glassdoor, Workday, Handshake, and most job boards.

---

## Excel Spreadsheet Format

Logs to your configured Excel spreadsheet path (set in `server.py`)

| Job Applied | Date | Pay | Resume | Follow Up |
|---|---|---|---|---|
| Data Analyst | 2026-05-15 | 60k – 80k | Resume_v3.pdf | Apply by Friday |

---

## Requirements

- Python 3.x
- Google Chrome
- macOS (LaunchAgent auto-start is Mac-specific)

Python packages (installed automatically by `setup.sh`):
```
flask
flask-cors
openpyxl
```

---

## Server Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Check if server is running |
| `/resumes` | GET | Returns list of PDFs from Resume Versions folder |
| `/log` | POST | Appends a new row to the Excel spreadsheet |

---

## Troubleshooting

**Extension shows "Server not reachable"**
- The server may not be running. Start it manually:
  ```bash
  python3 server.py
  ```
- Or check the LaunchAgent logs:
  ```bash
  cat ~/Library/Logs/jobtracker.error.log
  ```

**Re-install the LaunchAgent after moving the project folder**
```bash
bash setup.sh
```

**Check server is live**
```bash
curl http://localhost:5050/health
```
