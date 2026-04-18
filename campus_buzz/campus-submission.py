import json
import requests
from tablestore import *

OTS_ENDPOINT = 'https://campusbuzz-db.cn-hangzhou.ots.aliyuncs.com'
OTS_ID = 'LTAI5tP48EfiSHNBXArfz5oC'
OTS_SECRET = 'AsCOzNK16KOfEePjXzz7t11TICNhZ3'
OTS_INSTANCE = 'campusbuzz-db'
client = OTSClient(OTS_ENDPOINT, OTS_ID, OTS_SECRET, OTS_INSTANCE)


def handler(event, context):
    try:
        # --- 核心逻辑：全能解析 event ---
        if isinstance(event, (str, bytes)):
            payload = json.loads(event)
        else:
            payload = event

        # 如果是通过 HTTP 触发器调用的，数据在 payload['body'] 里
        if 'body' in payload:
            print("Detected HTTP Trigger...")
            # HTTP 触发器的 body 有可能是 base64 或 字符串
            body_data = payload['body']
            if payload.get('isBase64Encoded'):
                import base64
                body_data = base64.b64decode(body_data).decode('utf-8')

            # 再次解析 body 字符串为 JSON
            if isinstance(body_data, str):
                inner_data = json.loads(body_data)
            else:
                inner_data = body_data
            eid = inner_data.get('event_id')
        else:
            # 手动测试或普通调用
            print("Detected Manual Test...")
            eid = payload.get('event_id')

        print(f"Final Event ID parsed: {eid}")

        if not eid:
            print("ERROR: Could not find event_id in any field!")
            return "Fail: No ID"

        # 执行数据库查询并传球给 B (后面逻辑不变)
        primary_key = [('event_id', str(eid))]
        _, row, _ = client.get_row('events', primary_key)

        if row:
            data = {attr[0]: attr[1] for attr in row.attribute_columns}
            data['event_id'] = eid
            NEXT_URL = "https://campus-ocessing-cigsygcntq.cn-hangzhou.fcapp.run"
            # 增加一个 print 确认 B 的返回状态
            resp = requests.post(NEXT_URL, json=data, timeout=5)
            print(f"Sent to B. B returned: {resp.status_code}")
            return f"Success: Triggered B for {eid}"

        return "Fail: Row not in DB"

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return str(e)