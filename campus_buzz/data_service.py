from flask import Flask, request, jsonify
from tablestore import *

app = Flask(__name__)

# 填写你的 Tablestore 配置
OTS_ENDPOINT = 'https://campusbuzz-db.cn-hangzhou.ots.aliyuncs.com'
OTS_ID = ''
OTS_SECRET = ''
OTS_INSTANCE = 'campusbuzz-db'
client = OTSClient(OTS_ENDPOINT, OTS_ID, OTS_SECRET, OTS_INSTANCE)

@app.route('/api/data/save', methods=['POST'])
def save():
    data = request.json
    pk = [('event_id', data['event_id'])]
    attrs = [('title', data['title']), ('description', data['description']),
             ('location', data['location']), ('date', data['date']),
             ('organiser', data['organiser']), ('status', data['status'])]
    client.put_row('events', Row(pk, attrs))
    return jsonify({"status": "success"}), 200

@app.route('/api/data/update', methods=['POST'])
def update():
    data = request.json
    pk = [('event_id', data['event_id'])]
    update_cols = {'PUT': [
        ('status', data.get('status')), ('category', data.get('category')),
        ('priority', data.get('priority')), ('explanation', data.get('explanation'))
    ]}
    client.update_row('events', Row(pk, update_cols), Condition(RowExistenceExpectation.IGNORE))
    return jsonify({"status": "updated"}), 200

@app.route('/api/data/get/<event_id>', methods=['GET'])
def get(event_id):
    pk = [('event_id', event_id)]
    _, row, _ = client.get_row('events', pk)
    if not row: return jsonify({"error": "not found"}), 404
    res = {attr[0]: attr[1] for attr in row.attribute_columns}
    return jsonify(res), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
