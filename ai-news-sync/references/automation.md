# 定时任务配置指南

## 概述

本文档说明如何配置WorkBuddy自动化任务，实现定时同步AI资讯。

## 自动化目录结构

```
工作目录/
└── .codebuddy/
    └── automations/
        └── {automation-id}/
            ├── automation.toml    # 自动化配置
            └── memory.md          # 执行历史记录
```

## automation.toml 配置

```toml
version = 1
id = "ai-news-sync"
name = "AI资讯每日同步"
status = "ACTIVE"
rrule = "FREQ=DAILY;BYHOUR=17;BYMINUTE=30"
cwds = ["c:\\Users\\YourName\\WorkBuddy\\Claw"]
model_id = "glm-5.0"
model_is_thinking = true
```

### 配置项说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `version` | 配置版本 | `1` |
| `id` | 自动化ID（唯一） | `"ai-news-sync"` |
| `name` | 显示名称 | `"AI资讯每日同步"` |
| `status` | 状态 | `"ACTIVE"` 或 `"PAUSED"` |
| `rrule` | 调度规则（iCalendar格式） | `"FREQ=DAILY;BYHOUR=17;BYMINUTE=30"` |
| `cwds` | 工作目录列表 | `["/path/to/workspace"]` |

## 调度规则 (rrule)

### 每日执行

```toml
# 每天17:30执行
rrule = "FREQ=DAILY;BYHOUR=17;BYMINUTE=30"
```

### 每周执行

```toml
# 每周一9:00执行
rrule = "FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0"

# 每周一、三、五18:00执行
rrule = "FREQ=WEEKLY;BYDAY=MO,WE,FR;BYHOUR=18;BYMINUTE=0"
```

### 每小时执行

```toml
# 每小时执行
rrule = "FREQ=HOURLY;INTERVAL=1"

# 每2小时执行
rrule = "FREQ=HOURLY;INTERVAL=2"
```

## memory.md 格式

```markdown
# 自动化任务执行记录

## 配置信息
- ID: ai-news-sync
- 名称: AI资讯每日同步
- 调度: 每日 17:30

---

## 执行历史

### 2026-03-19 17:30
**状态**: 成功

**执行结果**:
- Obsidian: ✅ 成功
- Notion: ✅ 10/10 成功
- IMA: ✅ 成功

**摘要**: 同步10条AI资讯到三平台

### 2026-03-18 17:30
...
```

## 两阶段定时任务

当用户说"几点给我更新"时，采用两阶段模式：

### 阶段一：立即保存本地

```python
# 立即执行
python sync_ai_news.py local
```

### 阶段二：创建定时任务同步云端

1. 创建自动化配置：

```toml
version = 1
id = "ai-news-cloud-sync"
name = "AI资讯云端同步"
status = "ACTIVE"
rrule = "FREQ=DAILY;BYHOUR=18;BYMINUTE=0"
cwds = ["工作目录路径"]
```

2. 到点自动执行：

```python
python sync_ai_news.py cloud
```

## 使用 automation_update 工具

通过WorkBuddy的 automation_update 工具管理自动化：

### 查看自动化

```python
automation_update(
    mode="view",
    id="ai-news-sync"
)
```

### 创建自动化

```python
automation_update(
    mode="suggested create",
    name="AI资讯每日同步",
    prompt="获取最新10条AI资讯并同步到Notion和IMA",
    rrule="FREQ=DAILY;BYHOUR=17;BYMINUTE=30",
    cwds='["/path/to/workspace"]',
    status="ACTIVE"
)
```

### 更新自动化

```python
automation_update(
    mode="suggested update",
    id="ai-news-sync",
    status="PAUSED"  # 暂停
)
```

## 注意事项

1. **时区**：时间使用用户本地时区
2. **工作目录**：确保脚本在正确的工作目录下
3. **凭证配置**：脚本中的凭证需要提前配置好
4. **执行日志**：每次执行后更新 memory.md 记录结果
