import json
from tablestore import *

OTS_ENDPOINT = 'https://campusbuzz-db.cn-hangzhou.ots.aliyuncs.com'
OTS_ID = 'LTAI5tP48EfiSHNBXArfz5oC'
OTS_SECRET = 'AsCOzNK16KOfEePjXzz7t11TICNhZ3'
OTS_INSTANCE = 'campusbuzz-db'
client = OTSClient(OTS_ENDPOINT, OTS_ID, OTS_SECRET, OTS_INSTANCE)


def handler(event, context):
    try:
        # Core: Analyze the packaging data sent from B
        if isinstance(event, (str, bytes)):
            payload = json.loads(event)
        else:
            payload = event

        if 'body' in payload:
            body_data = payload['body']
            if payload.get('isBase64Encoded'):
                import base64
                body_data = base64.b64decode(body_data).decode('utf-8')
            res = json.loads(body_data) if isinstance(body_data, str) else body_data
        else:
            res = payload

        eid = res.get('event_id')
        if not eid: return "Error: No ID"

        # Carry out the update
        primary_key = [('event_id', str(eid))]
        update_cols = {'PUT': [
            ('status', res.get('status')), ('category', res.get('category')),
            ('priority', res.get('priority')), ('explanation', res.get('explanation'))
        ]}
        client.update_row('events', Row(primary_key, update_cols), Condition(RowExistenceExpectation.IGNORE))
        print(f"C Success: Updated {eid}")
        return f"Final Success: {eid}"

    except Exception as e:
        print(f"C Error: {str(e)}")
        return str(e)