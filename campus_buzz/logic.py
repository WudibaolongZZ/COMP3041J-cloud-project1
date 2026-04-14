import re
from datetime import datetime


def process_event(data):
    # 1. 检查字段完整性
    required_fields = ['title', 'description', 'location', 'date', 'organiser']
    for field in required_fields:
        if not data.get(field) or str(data.get(field)).strip() == "":
            return {
                "status": "INCOMPLETE",
                "category": "GENERAL",
                "priority": "NORMAL",
                "explanation": f"Missing required field: {field}"
            }

    # 2. 检查日期格式 (YYYY-MM-DD)
    date_str = data.get('date')
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        date_valid = True
    except ValueError:
        date_valid = False

    # 3. 检查描述长度
    desc_text = data.get('description', '')
    desc_valid = len(desc_text) >= 40

    # 判断是否需要修改 (只要日期或长度有一个不对)
    if not date_valid or not desc_valid:
        explanation = []
        if not date_valid: explanation.append("Date format must be YYYY-MM-DD.")
        if not desc_valid: explanation.append("Description must be at least 40 characters.")
        return {
            "status": "NEEDS REVISION",
            "category": "GENERAL",
            "priority": "NORMAL",
            "explanation": " ".join(explanation)
        }

    # 4. 关键词分类逻辑 (注意顺序)
    # 合并标题和描述进行搜索
    full_text = (data['title'] + " " + data['description']).lower()

    # 规则：Opportunity > Academic > Social
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

    return {
        "status": "APPROVED",
        "category": category,
        "priority": priority,
        "explanation": "All checks passed. Event is approved for posting."
    }


# --- 简单测试一下 ---
sample = {
    "title": "Big Tech Recruitment",
    "description": "This is a very long description to ensure that we meet the forty characters requirement for the campus buzz project.",
    "location": "Room 404",
    "date": "2024-10-20",
    "organiser": "Student Union"
}
print(process_event(sample))