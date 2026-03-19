# AI资讯同步技能 (ai-news-sync)

## 简介

AI资讯同步工具 - 自动获取最新AI资讯，同步到Obsidian/Notion/IMA多平台，支持定时任务和知识中枢工作流。

## 功能特性

- **多平台同步**：Obsidian本地 → Notion数据库 → IMA笔记
- **定时任务**：支持自动化定时执行
- **两阶段模式**：立即保存本地，定时同步云端
- **完整文档**：包含API参考和配置指南

## 安装方法

### 方法一：通过WorkBuddy安装

1. 将 `ai-news-sync.zip` 解压到 `~/.workbuddy/skills/` 目录（用户级）或项目的 `.workbuddy/skills/` 目录（项目级）
2. 重启WorkBuddy或重新加载技能

### 方法二：手动安装

1. 解压 `ai-news-sync.zip`
2. 将整个 `ai-news-sync` 文件夹复制到：
   - 用户级：`C:\Users\你的用户名\.workbuddy\skills\`
   - 项目级：`你的项目目录\.workbuddy\skills\`

## 目录结构

```
ai-news-sync/
├── SKILL.md                    # 技能主文档
├── scripts/
│   └── sync_ai_news.py         # 核心同步脚本
├── references/
│   ├── notion_api.md           # Notion API文档
│   ├── ima_api.md              # IMA API文档
│   └── automation.md           # 定时任务配置指南
└── assets/                     # 资源文件（预留）
```

## 快速开始

### 1. 配置凭证

编辑 `scripts/sync_ai_news.py`，填入你的凭证：

```python
NOTION_TOKEN = "ntn_你的Notion令牌"
NOTION_DB_ID = "你的数据库ID"
IMA_CLIENT_ID = "你的IMA ClientID"
IMA_API_KEY = "你的IMA API Key"
IMA_NOTE_ID = "你的IMA笔记ID"
OBSIDIAN_PATH = r"C:\Users\你的用户名\Documents\Obsidian Vault\Insights"
```

### 2. 配置Notion数据库

创建Notion数据库，包含以下属性：

| 属性名 | 类型 |
|--------|------|
| 标题 | Title |
| 来源 | URL |
| 摘要 | Text |
| 正文 | Text |
| 标签 | Multi-select |

### 3. 获取凭证

#### Notion
1. 访问 https://www.notion.so/my-integrations
2. 创建集成，获取 Token
3. 在目标数据库页面添加连接

#### IMA
1. 访问 https://ima.qq.com 开放平台
2. 申请开发者权限
3. 创建应用获取 ClientID 和 API Key

### 4. 运行同步

```bash
# 完整同步
python scripts/sync_ai_news.py

# 仅保存本地
python scripts/sync_ai_news.py local

# 仅同步云端
python scripts/sync_ai_news.py cloud
```

## 使用方式

### 手动执行

告诉WorkBuddy：
- "获取最新AI资讯"
- "同步AI新闻到Notion和IMA"

### 定时任务

告诉WorkBuddy：
- "每天17:30给我更新AI资讯"
- "18点更新下最热门的10条新闻资讯"

WorkBuddy会自动：
1. 立即获取资讯并保存到本地
2. 创建定时任务到指定时间同步云端

## 技术要点

### IMA API 重要说明

IMA API成功时返回 `{"doc_id": "..."}`，不是 `{"code": 0}`。

```python
# 正确判断
if response.get('doc_id'):
    return True  # 成功

# 错误判断
if response.get('code') == 0:
    return True  # 这个是错的！
```

### Notion API 属性映射

```python
"标题": {"title": [{"text": {"content": "..."}}]}
"来源": {"url": "https://..."}
"摘要": {"rich_text": [{"text": {"content": "..."}}]}
"标签": {"multi_select": [{"name": "AI/大模型"}]}
```

## 常见问题

### Q: IMA同步显示失败但实际成功？
A: 检查判断逻辑，应检查 `doc_id` 而非 `code`。

### Q: Notion数据库字段不匹配？
A: 确保属性名称和类型与脚本中定义的一致。

### Q: 定时任务不执行？
A: 检查 `.codebuddy/automations/` 下的配置文件，确保 `status = "ACTIVE"`。

## 版本信息

- 版本：1.0.0
- 创建日期：2026-03-19
- 兼容：WorkBuddy 1.x

## 许可证

MIT License - 可自由使用、修改和分发

## 支持

如有问题，请提交issue或者私信反馈。
