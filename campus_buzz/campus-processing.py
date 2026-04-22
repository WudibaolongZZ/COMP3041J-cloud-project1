import json
import requests
import base64
from datetime import datetime


def handler(event, context):
    try:
        # 1. Parse packaging data (supports multiple calling sources)
        if isinstance(event, (str, bytes)):
            payload = json.loads(event)
        else:
            payload = event

        if 'body' in payload:
            body_data = payload['body']
            if payload.get('isBase64Encoded'):
                body_data = base64.b64decode(body_data).decode('utf-8')
            data = json.loads(body_data) if isinstance(body_data, str) else body_data
        else:
            data = payload

        eid = data.get('event_id')

        # 2. Strict integrity check (highest priority: Rule 1)
        required_fields = ['title', 'description', 'location', 'date', 'organiser']
        missing = [f for f in required_fields if not data.get(f) or str(data.get(f)).strip() == ""]

        if missing:
            status = "INCOMPLETE"
            # When the integrity check fails, classification should not be carried out.
            category = "N/A"
            priority = "N/A"
            note = f"Required field(s) missing: {', '.join(missing)}. Audit halted."
        else:
            # 3. Detailed format and length check (Medium priority: Rules 2 & 3)
            title = data.get('title', '')
            desc = data.get('description', '')
            date_str = data.get('date', '')

            revision_reasons = []

            # Verify the date format
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except:
                revision_reasons.append("Date format must be YYYY-MM-DD.")

            # Verify the description length
            if len(desc) < 40:
                revision_reasons.append(f"Description too short ({len(desc)}/40 chars).")

            if revision_reasons:
                status = "NEEDS REVISION"
                # When the format check fails, classification should not be carried out either.
                category = "N/A"
                priority = "N/A"
                note = " ".join(revision_reasons)
            else:
                # 4. Classification logic (lowest priority: execution is only carried out when all fields are complete and in correct format)
                full_text = (title + " " + desc).lower()

                # Strictly follow the priority order specified in the document (Rule 4)
                if any(k in full_text for k in ['career', 'internship', 'recruitment']):
                    category = "OPPORTUNITY"
                    priority = "HIGH"
                elif any(k in full_text for k in ['workshop', 'seminar', 'lecture']):
                    category = "ACADEMIC"
                    priority = "MEDIUM"
                elif any(k in full_text for k in ['club', 'society', 'social']):
                    category = "SOCIAL"
                    priority = "NORMAL"
                else:
                    category = "GENERAL"
                    priority = "NORMAL"

                status = "APPROVED"
                note = "All checks passed successfully."

        # 5. Package the result and pass it to function C
        result = {
            "event_id": eid,
            "status": status,
            "category": category,
            "priority": priority,
            "explanation": note
        }

        # Debug log: Ensure that the logical output can be seen in the console.
        print(f"Audit Complete for {eid}: Status={status}, Category={category}")

        UPDATE_URL = "https://campus-update-kiukrcarwl.cn-hangzhou.fcapp.run"
        resp = requests.post(UPDATE_URL, json=result, timeout=5)

        return f"Processed as {status}: {note}"

    except Exception as e:
        print(f"B Error: {str(e)}")
        return str(e)