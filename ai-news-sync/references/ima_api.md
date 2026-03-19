# IMA API 参考文档

## 概述

IMA（QQ笔记）开放平台API用于将AI资讯同步到IMA笔记。本文档包含追加笔记内容所需的全部API信息。

## 认证

### 获取凭证

1. 访问 [IMA开放平台](https://ima.qq.com)
2. 申请开发者权限
3. 创建应用获取 `ClientID` 和 `API Key`

### 认证方式

API调用时需要通过HTTP头传递认证信息：

```
ima-openapi-clientid: {ClientID}
ima-openapi-apikey: {API Key}
```

## 笔记ID获取

笔记ID是笔记URL中的数字部分：

```
https://ima.qq.com/note/7440300159009249
                        ^^^^^^^^^^^^^^^
                        这就是笔记ID
```

## 追加内容API

### 请求

```
POST https://ima.qq.com/openapi/note/v1/append_doc
```

### 请求头

```
Content-Type: application/json
ima-openapi-clientid: {ClientID}
ima-openapi-apikey: {API Key}
```

### 请求体结构

```json
{
  "doc_id": "笔记ID",
  "content_format": 1,
  "content": "要追加的内容（支持Markdown）"
}
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `doc_id` | string | 笔记ID，URL中的数字 |
| `content_format` | int | 内容格式：1=Markdown, 2=纯文本 |
| `content` | string | 要追加的内容 |

## 响应

### ⚠️ 重要：成功响应格式

**IMA API成功时返回的是 `{"doc_id": "..."}` 而非 `{"code": 0}`！**

```json
{
  "doc_id": "7440300159009249"
}
```

### 失败响应

```json
{
  "code": 400,
  "errmsg": "错误描述"
}
```

## 正确的判断逻辑

```python
# ❌ 错误：不要检查code字段
if response.get('code') == 0:
    return True

# ✅ 正确：检查doc_id字段
if response.get('doc_id'):
    return True
```

## Python调用示例

```python
import subprocess
import json

def ima_append(content, note_id, client_id, api_key):
    body = {
        "doc_id": note_id,
        "content_format": 1,  # Markdown格式
        "content": content
    }
    
    cmd = [
        "curl", "-s", "-X", "POST",
        "https://ima.qq.com/openapi/note/v1/append_doc",
        "-H", "Content-Type: application/json",
        "-H", f"ima-openapi-clientid: {client_id}",
        "-H", f"ima-openapi-apikey: {api_key}",
        "-d", json.dumps(body, ensure_ascii=False)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    response = json.loads(result.stdout)
    
    # 关键：检查doc_id而非code
    if response.get('doc_id'):
        return True, response['doc_id']
    else:
        return False, response.get('errmsg', 'Unknown error')
```

## 常见错误

| 错误 | 说明 | 解决方案 |
|------|------|---------|
| 无效的API Key | 认证失败 | 检查ClientID和API Key |
| 笔记不存在 | doc_id错误 | 确认笔记ID正确 |
| 权限不足 | 未授权访问 | 确认应用有权限访问该笔记 |

## 最佳实践

1. **追加前添加分隔**：使用 `\n\n` 在新内容前添加空行
2. **内容长度**：单次追加内容不宜过长，建议分批处理
3. **错误处理**：始终检查 `doc_id` 字段判断成功
4. **超时设置**：建议设置60秒超时

## 参考链接

- [IMA开放平台](https://ima.qq.com)
- API文档：登录开放平台后查看
