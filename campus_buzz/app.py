from flask import Flask, request, render_template, jsonify
import uuid
import requests
from tablestore import *

app = Flask(__name__)

# --- 1. 阿里云参数配置 ---
OTS_ENDPOINT = 'https://campusbuzz-db.cn-hangzhou.ots.aliyuncs.com'
OTS_ID = 'LTAI5tP48EfiSHNBXArfz5oC'
OTS_SECRET = 'AsCOzNK16KOfEePjXzz7t11TICNhZ3'
OTS_INSTANCE = 'campusbuzz-db'

# 你的第一个函数 (Submission Event Function) 的 URL
FC_SUBMISSION_URL = "https://campus-bmission-dnlxjedizq.cn-hangzhou.fcapp.run"

# 初始化数据库客户端 (Data Service 组件角色)
client = OTSClient(OTS_ENDPOINT, OTS_ID, OTS_SECRET, OTS_INSTANCE)


# --- 2. Data Service 组件：存入初始记录 ---
def save_to_db(data):
    primary_key = [('event_id', data['event_id'])]
    attribute_columns = [
        ('title', data['title']),
        ('description', data['description']),
        ('location', data['location']),
        ('date', data['date']),
        ('organiser', data['organiser']),
        ('status', data['status'])
    ]
    try:
        client.put_row('events', Row(primary_key, attribute_columns))
        print(f"[Data Service] Saved {data['event_id']} to Tablestore")
        return True
    except Exception as e:
        print(f"Data Service Error: {e}")
        return False







# --- 3. Presentation Service 组件：显示表单 ---
@app.route('/')
def index():
    return render_template('index.html')


# --- 4. Workflow Service 组件：处理提交并触发函数 ---
@app.route('/submit', methods=['POST'])
def submit():
    event_id = str(uuid.uuid4())
    # 获取表单数据并初始化状态为 PENDING
    event_data = {
        "event_id": event_id,
        "title": request.form.get('title'),
        "description": request.form.get('description'),
        "location": request.form.get('location'),
        "date": request.form.get('date'),
        "organiser": request.form.get('organiser'),
        "status": "PENDING"
    }

    # 第一步：存入数据库
    if save_to_db(event_data):
        # 第二步：触发 Serverless 工作流
        # --- 修改这一段进行调试 ---
        try:
            # 增加 timeout 到 5 秒，看看是不是因为 1 秒太短了导致断开
            response = requests.post(FC_SUBMISSION_URL, json={"event_id": event_id}, timeout=5)
            print(f"[Trigger] Status Code: {response.status_code}")
            print(f"[Trigger] Response: {response.text}")
        except Exception as e:
            print(f"[Trigger] CRITICAL ERROR: {str(e)}")

        # 创建结果字典用于渲染result.html
        result = {
            'status': 'PENDING',
            'category': '—',
            'priority': '—',
            'event_id': event_id,
            'note': 'Your submission is being processed. Please wait for the audit to complete.',
            'title': event_data['title'],
            'description': event_data['description'],
            'location': event_data['location'],
            'date': event_data['date'],
            'organiser': event_data['organiser']
        }
        return render_template('result.html', result=result)
    return "Error: Could not save to database."


# --- 5. Presentation/Data Service 组合：查询真实结果 ---
@app.route('/results/<event_id>')
def get_results(event_id):
    """
    此路由非常关键！它会读取由函数计算更新后的真实数据。
    如果你的函数 C 没工作，这里永远会显示 PENDING。
    """
    primary_key = [('event_id', event_id)]
    try:
        _, row, _ = client.get_row('events', primary_key)
        if not row:
            return "Record not found."

        # 将结果列转为字典
        # 加上一个 _ 来忽略掉多出来的那个时间戳参数
        res = {attr[0]: attr[1] for attr in row.attribute_columns}
        # 返回符合项目要求的 4 个核心字段
        return jsonify({
            "event_id": event_id,
            "final_status": res.get('status'),
            "category": res.get('category', 'Waiting...'),
            "priority": res.get('priority', 'Waiting...'),
            "review_note": res.get('explanation', 'Background processing...')
        })
    except Exception as e:
        return f"Query failed: {str(e)}"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
