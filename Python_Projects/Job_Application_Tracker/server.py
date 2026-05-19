from flask import Flask, request, jsonify
from flask_cors import CORS
import openpyxl
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

EXCEL_PATH = '/Users/jorgereyeso/Documents/Applications spreadsheet.xlsx'
RESUMES_DIR = '/Users/jorgereyeso/Documents/Resumes/Resume Versions'


@app.route('/health')
def health():
    return jsonify({'status': 'running'})


@app.route('/resumes')
def get_resumes():
    try:
        files = sorted([
            f for f in os.listdir(RESUMES_DIR)
            if f.endswith(('.pdf', '.docx')) and not f.startswith('~$')
        ])
        return jsonify({'resumes': files})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/log', methods=['POST'])
def log_application():
    try:
        data = request.json
        wb = openpyxl.load_workbook(EXCEL_PATH)
        ws = wb.active
        ws.append([
            data.get('job_title', ''),
            datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            data.get('pay', ''),
            data.get('resume', ''),
            data.get('follow_up', '')
        ])
        wb.save(EXCEL_PATH)
        return jsonify({'status': 'ok', 'row': ws.max_row})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5050, debug=False)
