import re
from datetime import datetime


def audit_event(data):
    # 1. 检查必填项
    required_fields = ['title', 'description', 'location', 'date', 'organiser']
    for field in required_fields:
        if not data.get(field):
            return {"status": "INCOMPLETE", "category": "GENERAL", "priority": "NORMAL",
                    "note": f"Missing field: {field}"}

    # 2. 检查日期格式 (YYYY-MM-DD)
    try:
        datetime.strptime(data['date'], '%Y-%m-%d')
    except ValueError:
        return {"status": "NEEDS REVISION", "category": "GENERAL", "priority": "NORMAL",
                "note": "Invalid date format. Use YYYY-MM-DD."}

    # 3. 检查描述长度
    if len(data['description']) < 40:
        return {"status": "NEEDS REVISION", "category": "GENERAL", "priority": "NORMAL",
                "note": "Description must be at least 40 characters."}

    # 4. 关键词分类逻辑 (注意顺序优先)
    desc = (data['title'] + " " + data['description']).lower()

    if any(k in desc for k in ['career', 'internship', 'recruitment']):
        category = "OPPORTUNITY"
        priority = "HIGH"
    elif any(k in desc for k in ['workshop', 'seminar', 'lecture']):
        category = "ACADEMIC"
        priority = "MEDIUM"
    elif any(k in desc for k in ['club', 'society', 'social']):
        category = "SOCIAL"
        priority = "NORMAL"
    else:
        category = "GENERAL"
        priority = "NORMAL"

    return {
        "status": "APPROVED",
        "category": category,
        "priority": priority,
        "note": "All checks passed successfully."
    }


# 测试一下
test_data = {
    "title": "Summer Internship",
    "description": "Join our amazing summer internship program to develop your career skills and more.",
    "location": "Online",
    "date": "2024-06-01",
    "organiser": "Tech Corp"
}
print(audit_event(test_data))