from flask import Flask, request, jsonify
import uuid, requests

app = Flask(__name__)

# 云端内部通信：使用容器服务名
DATA_SERVICE_URL = "http://data-service:5002/api/data/save"
FC_SUBMISSION_URL = "https://campus-bmission-dnlxjedizq.cn-hangzhou.fcapp.run"

@app.route('/api/workflow/submit', methods=['POST'])
def handle_workflow():
    raw_data = request.json
    event_id = str(uuid.uuid4())
    event_data = {**raw_data, "event_id": event_id, "status": "PENDING"}

    db_resp = requests.post(DATA_SERVICE_URL, json=event_data)
    if db_resp.status_code == 200:
        try:
            # 触发第一个 FC 函数
            requests.post(FC_SUBMISSION_URL, json={"event_id": event_id}, timeout=1)
        except: pass
        return jsonify({"event_id": event_id}), 200
    return jsonify({"error": "DB Save Failed"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)