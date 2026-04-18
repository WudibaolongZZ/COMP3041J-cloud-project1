import json
import requests
import base64
from datetime import datetime


def handler(event, context):
    try:
        # --- 1. 解析包装数据 (支持多种调用来源) ---
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

        # --- 2. 严格的完整性检查 (最高优先级: Rule 1) ---
        required_fields = ['title', 'description', 'location', 'date', 'organiser']
        missing = [f for f in required_fields if not data.get(f) or str(data.get(f)).strip() == ""]

        if missing:
            status = "INCOMPLETE"
            # 当完整性校验失败时，不应进行分类
            category = "N/A"
            priority = "N/A"
            note = f"Required field(s) missing: {', '.join(missing)}. Audit halted."
        else:
            # --- 3. 详细的格式与长度检查 (中优先级: Rule 2 & 3) ---
            title = data.get('title', '')
            desc = data.get('description', '')
            date_str = data.get('date', '')

            revision_reasons = []

            # 验证日期格式
            try:
                datetime.strptime(date_str, '%Y-%m-%d')
            except:
                revision_reasons.append("Date format must be YYYY-MM-DD.")

            # 验证描述长度
            if len(desc) < 40:
                revision_reasons.append(f"Description too short ({len(desc)}/40 chars).")

            if revision_reasons:
                status = "NEEDS REVISION"
                # 当格式校验失败时，同样不应进行分类
                category = "N/A"
                priority = "N/A"
                note = " ".join(revision_reasons)
            else:
                # --- 4. 分类逻辑 (最低优先级: 只有字段齐全且格式正确才执行) ---
                full_text = (title + " " + desc).lower()

                # 严格按照文档要求的优先级顺序 (Rule 4)
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

        # --- 5. 封装结果并传递给函数 C ---
        result = {
            "event_id": eid,
            "status": status,
            "category": category,
            "priority": priority,
            "explanation": note
        }

        # 调试日志：确保在控制台能看到逻辑输出
        print(f"Audit Complete for {eid}: Status={status}, Category={category}")

        UPDATE_URL = "https://campus-update-kiukrcarwl.cn-hangzhou.fcapp.run"
        resp = requests.post(UPDATE_URL, json=result, timeout=5)

        return f"Processed as {status}: {note}"

    except Exception as e:
        print(f"B Error: {str(e)}")
        return str(e)