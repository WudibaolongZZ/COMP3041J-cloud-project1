from flask import Flask, request, render_template, jsonify
import uuid
import requests # 用来调用其他服务和函数

app = Flask(__name__)

# 模拟 Data Service 的内部逻辑 (实际项目中这些可以拆分到不同容器)
# 注意：这里需要安装 tablestore 库，稍后在 Docker 部分我会讲
DATABASE_URL = "你的Tablestore私网地址"

# --- Component 1: Presentation Service (路由) ---
@app.route('/')
def index():
    # 返回一个简单的 HTML 表单页面
    return '''
        <h1>Campus Buzz - Submit Event</h1>
        <form action="/submit" method="post">
            Title: <input type="text" name="title"><br>
            Description: <textarea name="description"></textarea><br>
            Location: <input type="text" name="location"><br>
            Date (YYYY-MM-DD): <input type="text" name="date"><br>
            Organiser: <input type="text" name="organiser"><br>
            <input type="submit" value="Submit">
        </form>
    '''

# --- Component 2: Workflow Service (路由) ---
@app.route('/submit', methods=['POST'])
def submit():
    # 1. 获取表单数据
    data = {
        "event_id": str(uuid.uuid4()), # 生成唯一ID
        "title": request.form.get('title'),
        "description": request.form.get('description'),
        "location": request.form.get('location'),
        "date": request.form.get('date'),
        "organiser": request.form.get('organiser'),
        "status": "PENDING" # 初始状态
    }

    # 2. 调用 Data Service 存储初始记录
    # 这里我们简化为直接调用保存函数
    save_to_db(data)

    # 3. 关键：触发第一个 Serverless 函数 (Submission Event Function)
    # 你需要替换成你阿里云函数的触发地址
    FC_URL = "https://你的函数触发链接.fc.aliyuncs.com"
    try:
        requests.post(FC_URL, json=data, timeout=5)
    except:
        pass # 后台触发，不需要等待结果

    return f"Event submitted! Your ID is: {data['event_id']}. Please check back in a few seconds."

# --- Component 3: Data Service (内部存储逻辑) ---
def save_to_db(data):
    # 这里写连接 Tablestore 的逻辑
    # 暂时用 print 模拟，后续我们会补全 SDK 代码
    print(f"[Data Service] Saving record: {data['event_id']}")
    return True

@app.route('/results/<event_id>')
def get_results(event_id):
    # 从数据库读取结果并显示
    # 模拟返回
    return jsonify({"status": "APPROVED", "category": "ACADEMIC", "priority": "MEDIUM"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)