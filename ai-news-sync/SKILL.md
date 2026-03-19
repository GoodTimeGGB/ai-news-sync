---
name: ai-news-sync
description: AI资讯同步技能，用于获取最新AI资讯并同步到多个平台（Obsidian本地、Notion数据库、IMA笔记）。支持手动执行和定时自动化。当用户需要获取AI新闻、同步资讯、创建知识中枢工作流时使用此技能。
---

# AI资讯同步技能

## 概述

此技能实现了AI资讯的知识中枢同步流程，支持：
- 从网络获取最新AI资讯（X/Twitter、Hacker News等）
- 保存到Obsidian本地Markdown文件
- 同步到Notion数据库
- 同步到IMA笔记
- 支持定时自动化任务

## 使用场景

当用户提出以下需求时触发此技能：
- "获取最新AI资讯"
- "同步AI新闻到Notion/IMA"
- "定时更新AI资讯"
- "创建知识中枢工作流"
- "几点给我更新新闻"（定时任务模式）

## 配置指南

### 1. 必需配置项

在使用此技能前，需要配置以下凭证：

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `NOTION_TOKEN` | Notion API令牌 | [Notion Developers](https://www.notion.so/my-integrations) 创建集成获取 |
| `NOTION_DB_ID` | Notion数据库ID | 打开数据库页面，URL中的32位字符串 |
| `IMA_CLIENT_ID` | IMA开放平台ClientID | [IMA开放平台](https://ima.qq.com) 申请获取 |
| `IMA_API_KEY` | IMA开放平台API Key | IMA开放平台申请获取 |
| `IMA_NOTE_ID` | IMA笔记ID | 笔记URL中的数字ID |
| `OBSIDIAN_PATH` | Obsidian本地路径 | 本地Obsidian Vault路径 |

### 2. Notion数据库配置

创建Notion数据库时，需要以下属性字段：

| 属性名 | 类型 | 说明 |
|--------|------|------|
| 标题 | Title | 资讯标题 |
| 来源 | URL | 原文链接 |
| 摘要 | Text | 资讯摘要（最多2000字符） |
| 正文 | Text | 完整内容 |
| 标签 | Multi-select | 分类标签，如"AI/大模型" |

### 3. 配置示例

将配置写入脚本的配置区域：

```python
# 配置信息
NOTION_TOKEN = "ntn_xxxxxxxxxxxxx"
NOTION_DB_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
IMA_CLIENT_ID = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
IMA_API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
IMA_NOTE_ID = "xxxxxxxxxxxxx"
OBSIDIAN_PATH = r"C:\Users\YourName\Documents\Obsidian Vault\Insights"
```

## 使用方法

### 模式一：完整同步

执行完整的同步流程：获取资讯 → Obsidian → Notion → IMA

```bash
python scripts/sync_ai_news.py
```

### 模式二：两阶段定时任务

当用户说"几点给我更新"时，采用两阶段模式：

**阶段一：立即获取并保存本地**
```bash
python scripts/sync_ai_news.py local
```

**阶段二：到点同步云端**
```bash
python scripts/sync_ai_news.py cloud
```

### 模式三：仅同步云端

已有本地文件，仅同步到Notion和IMA：
```bash
python scripts/sync_ai_news.py cloud
```

## 核心脚本说明

### sync_ai_news.py

主同步脚本，包含以下功能：

1. **获取资讯数据** - 从网络搜索最新AI资讯
2. **保存Obsidian** - 生成Markdown文件保存到本地
3. **同步Notion** - 通过API添加到Notion数据库
4. **同步IMA** - 通过API追加到IMA笔记

### 关键API调用

#### Notion API

```python
# 添加页面到数据库
POST https://api.notion.com/v1/pages
Headers:
  Authorization: Bearer {NOTION_TOKEN}
  Notion-Version: 2022-06-28
  Content-Type: application/json
```

#### IMA API

```python
# 追加内容到笔记
POST https://ima.qq.com/openapi/note/v1/append_doc
Headers:
  Content-Type: application/json
  ima-openapi-clientid: {IMA_CLIENT_ID}
  ima-openapi-apikey: {IMA_API_KEY}
```

**重要**：IMA API成功时返回 `{"doc_id": "..."}`，失败时返回 `{"code": xxx, "errmsg": "..."}`。判断成功应检查 `doc_id` 字段是否存在。

## 定时任务配置

### 使用WorkBuddy自动化

在工作目录创建 `.codebuddy/automations/` 目录，配置自动化任务：

```toml
# automation.toml
version = 1
id = "ai-news-sync"
name = "AI资讯每日同步"
status = "ACTIVE"
rrule = "FREQ=DAILY;BYHOUR=17;BYMINUTE=30"
cwds = ["工作目录路径"]
```

### 定时任务流程

1. 用户说"17:30给我更新AI资讯"
2. **立即执行**：获取最新资讯，保存到Obsidian本地
3. **创建自动化任务**：设置17:30执行云端同步
4. **到点执行**：自动同步到Notion和IMA

## 输出格式

### Obsidian Markdown格式

```markdown
# AI资讯更新 - 2026-03-19 18:00:00

**来源**: X（Twitter）和 Hacker News

---

## 1. 资讯标题

**来源**: 来源名称 | **日期**: 2026-03-19

资讯摘要内容...

**链接**: [原文链接](https://...)

---

...
```

### 执行结果

```json
{
  "status": "success",
  "obsidian": true,
  "notion": {"success": 10, "failed": 0},
  "ima": true,
  "timestamp": "2026-03-19 18:00:00",
  "file": "本地文件路径"
}
```

## 常见问题

### Q: IMA同步显示失败但实际成功？

A: IMA API成功返回的是 `{"doc_id": "..."}` 而非 `{"code": 0}`。确保判断逻辑正确：
```python
if response.get('doc_id'):  # 正确
    return True
# 而非
if response.get('code') == 0:  # 错误
    return True
```

### Q: Notion数据库字段不匹配？

A: 确保数据库有以下属性：标题(Title)、来源(URL)、摘要(Text)、正文(Text)、标签(Multi-select)

### Q: 定时任务不执行？

A: 检查 `.codebuddy/automations/` 目录下的配置文件，确保 `status = "ACTIVE"`

## 相关资源

- `references/notion_api.md` - Notion API详细文档
- `references/ima_api.md` - IMA API详细文档
- `scripts/sync_ai_news.py` - 完整同步脚本
