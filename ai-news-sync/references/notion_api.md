# Notion API 参考文档

## 概述

Notion API 用于将AI资讯同步到Notion数据库。本文档包含创建数据库页面所需的全部API信息。

## 认证

### 获取API令牌

1. 访问 [Notion Developers](https://www.notion.so/my-integrations)
2. 点击 "New integration"
3. 填写集成名称，选择关联的工作区
4. 创建后获取 "Internal Integration Token"（以 `ntn_` 开头）

### 数据库权限

创建集成后，需要将数据库与集成关联：

1. 打开目标数据库页面
2. 点击右上角 "..." → "Add connections"
3. 搜索并选择你创建的集成

## 数据库ID获取

数据库ID是数据库URL中的32位字符串：

```
https://www.notion.so/your-workspace/DATABASE_ID?v=xxxxx
                              ^^^^^^^^^^^^
                              这就是数据库ID
```

## 创建页面API

### 请求

```
POST https://api.notion.com/v1/pages
```

### 请求头

```
Authorization: Bearer {NOTION_TOKEN}
Notion-Version: 2022-06-28
Content-Type: application/json
```

### 请求体结构

```json
{
  "parent": {
    "database_id": "数据库ID"
  },
  "properties": {
    "标题": {
      "title": [
        {
          "text": {
            "content": "资讯标题"
          }
        }
      ]
    },
    "来源": {
      "url": "https://example.com"
    },
    "摘要": {
      "rich_text": [
        {
          "text": {
            "content": "摘要内容（最多2000字符）"
          }
        }
      ]
    },
    "正文": {
      "rich_text": [
        {
          "text": {
            "content": "完整正文内容"
          }
        }
      ]
    },
    "标签": {
      "multi_select": [
        {"name": "AI/大模型"}
      ]
    }
  }
}
```

## 数据库属性类型

| 属性类型 | Notion类型 | JSON结构 |
|---------|-----------|----------|
| 标题 | title | `{"title": [{"text": {"content": "..."}}]}` |
| URL | url | `{"url": "https://..."}` |
| 文本 | rich_text | `{"rich_text": [{"text": {"content": "..."}}]}` |
| 多选 | multi_select | `{"multi_select": [{"name": "..."}]}` |
| 日期 | date | `{"date": {"start": "2026-03-19"}}` |
| 数字 | number | `{"number": 123}` |
| 复选框 | checkbox | `{"checkbox": true}` |

## 响应

### 成功响应

```json
{
  "object": "page",
  "id": "页面ID",
  "created_time": "2026-03-19T10:00:00Z",
  "last_edited_time": "2026-03-19T10:00:00Z",
  "properties": { ... },
  "url": "https://www.notion.so/..."
}
```

### 失败响应

```json
{
  "object": "error",
  "status": 400,
  "code": "validation_error",
  "message": "具体错误信息"
}
```

## 常见错误

| 错误代码 | 说明 | 解决方案 |
|---------|------|---------|
| `unauthorized` | 缺少认证或权限 | 检查Token和数据库连接 |
| `validation_error` | 属性格式错误 | 检查属性名称和类型匹配 |
| `object_not_found` | 数据库不存在 | 检查数据库ID是否正确 |

## Python调用示例

```python
import subprocess
import json

def notion_add_page(title, url, summary, source, date):
    body = {
        "parent": {"database_id": "YOUR_DATABASE_ID"},
        "properties": {
            "标题": {"title": [{"text": {"content": title}}]},
            "来源": {"url": url},
            "摘要": {"rich_text": [{"text": {"content": summary}}]},
            "正文": {"rich_text": [{"text": {"content": f"来源: {source}\n日期: {date}\n\n{summary}"}}]},
            "标签": {"multi_select": [{"name": "AI/大模型"}]}
        }
    }
    
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://api.notion.com/v1/pages",
        "-H", "Authorization: Bearer YOUR_TOKEN",
        "-H", "Notion-Version: 2022-06-28",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(body, ensure_ascii=False)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    response = json.loads(result.stdout)
    
    if response.get('object') == 'page':
        return True, response.get('id')
    else:
        return False, response.get('message')
```

## 限流说明

- 每个集成平均每秒最多3个请求
- 超过限制会返回 `429 Too Many Requests`
- 建议在批量操作时添加延迟（如 `time.sleep(0.3)`）

## 参考链接

- [Notion API 官方文档](https://developers.notion.com/)
- [创建页面 API](https://developers.notion.com/reference/post-page)
- [数据库属性类型](https://developers.notion.com/reference/property-object)
