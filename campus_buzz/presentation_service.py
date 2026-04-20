from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)

WORKFLOW_URL = "http://workflow-service:5001/api/workflow/submit"
DATA_GET_URL = "http://data-service:5002/api/data/get/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    form_data = request.form.to_dict()
    resp = requests.post(WORKFLOW_URL, json=form_data)
    if resp.status_code == 200:
        event_id = resp.json()['event_id']
        result = {'status': 'PENDING', 'event_id': event_id, **form_data}
        return render_template('result.html', result=result)
    return "Submission Error", 500

@app.route('/results/<event_id>')
def get_results(event_id):
    resp = requests.get(DATA_GET_URL + event_id)
    if resp.status_code == 200:
        data = resp.json()
        return jsonify({
            "event_id": event_id,
            "final_status": data.get('status'),
            "category": data.get('category', 'N/A'),
            "priority": data.get('priority', 'N/A'),
            "review_note": data.get('explanation', 'Processing...')
        })
    return "Not ready or Error", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)