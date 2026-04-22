import json
import requests
from tablestore import *

OTS_ENDPOINT = 'https://campusbuzz-db.cn-hangzhou.ots.aliyuncs.com'
OTS_ID = ''
OTS_SECRET = ''
OTS_INSTANCE = 'campusbuzz-db'
client = OTSClient(OTS_ENDPOINT, OTS_ID, OTS_SECRET, OTS_INSTANCE)


def handler(event, context):
    try:
        # Core logic: Comprehensive parsing of event
        if isinstance(event, (str, bytes)):
            payload = json.loads(event)
        else:
            payload = event

        # If it is triggered by an HTTP request, the data is stored in the 'body' field of payload.
        if 'body' in payload:
            print("Detected HTTP Trigger...")
            # The body of the HTTP trigger can be either in base64 format or as a string.
            body_data = payload['body']
            if payload.get('isBase64Encoded'):
                import base64
                body_data = base64.b64decode(body_data).decode('utf-8')

            # Re-parse the "body" string into JSON format
            if isinstance(body_data, str):
                inner_data = json.loads(body_data)
            else:
                inner_data = body_data
            eid = inner_data.get('event_id')
        else:
            # Manual testing or ordinary invocation
            print("Detected Manual Test...")
            eid = payload.get('event_id')

        print(f"Final Event ID parsed: {eid}")

        if not eid:
            print("ERROR: Could not find event_id in any field!")
            return "Fail: No ID"

        # Execute the database query and pass it to B (the subsequent logic remains the same)
        primary_key = [('event_id', str(eid))]
        _, row, _ = client.get_row('events', primary_key)

        if row:
            data = {attr[0]: attr[1] for attr in row.attribute_columns}
            data['event_id'] = eid
            NEXT_URL = "https://campus-ocessing-cigsygcntq.cn-hangzhou.fcapp.run"
            # Add a print statement to confirm the return status of B
            resp = requests.post(NEXT_URL, json=data, timeout=5)
            print(f"Sent to B. B returned: {resp.status_code}")
            return f"Success: Triggered B for {eid}"

        return "Fail: Row not in DB"

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")
        return str(e)