# -*- coding: utf-8 -*-
"""
AI资讯同步脚本
知识中枢流程：Obsidian → Notion Database → IMA

使用方法：
  python sync_ai_news.py          # 完整同步
  python sync_ai_news.py local    # 仅保存本地
  python sync_ai_news.py cloud    # 仅同步云端

配置说明：
  请先配置下方的 NOTION_TOKEN、NOTION_DB_ID、IMA_CLIENT_ID、IMA_API_KEY、IMA_NOTE_ID、OBSIDIAN_PATH
"""

import subprocess
import json
from datetime import datetime
import os
import time
import sys

# ==================== 配置区域 ====================
# 请将以下配置项替换为您自己的凭证

NOTION_TOKEN = "ntn_YOUR_NOTION_TOKEN_HERE"      # Notion API令牌
NOTION_DB_ID = "YOUR_DATABASE_ID_HERE"           # Notion数据库ID（32位字符串）
IMA_CLIENT_ID = "YOUR_IMA_CLIENT_ID_HERE"        # IMA开放平台ClientID
IMA_API_KEY = "YOUR_IMA_API_KEY_HERE"            # IMA开放平台API Key
IMA_NOTE_ID = "YOUR_IMA_NOTE_ID_HERE"            # IMA笔记ID
OBSIDIAN_PATH = r"C:\Users\YourName\Documents\Obsidian Vault\Insights"  # Obsidian本地路径

# ==================== 资讯数据 ====================
# 可以手动更新，也可以通过API自动获取

ai_updates = [
    # 示例数据格式
    # {
    #     "title": "资讯标题",
    #     "source": "来源名称",
    #     "date": "2026-03-19",
    #     "summary": "资讯摘要内容...",
    #     "url": "https://example.com/article"
    # },
]

# ==================== 核心功能 ====================

def notion_add_page(title, url, summary, source, date, tag="AI/大模型"):
    """
    添加页面到Notion数据库
    
    参数:
        title: 资讯标题
        url: 原文链接
        summary: 资讯摘要
        source: 来源名称
        date: 发布日期
        tag: 标签
    
    返回:
        (success, result) - 成功返回(True, page_id)，失败返回(False, error_message)
    """
    body = {
        "parent": {"database_id": NOTION_DB_ID},
        "properties": {
            "标题": {"title": [{"text": {"content": title}}]},
            "来源": {"url": url},
            "摘要": {"rich_text": [{"text": {"content": summary[:2000] if len(summary) > 2000 else summary}}]},
            "正文": {"rich_text": [{"text": {"content": f"来源: {source}\n日期: {date}\n\n{summary}"}}]},
            "标签": {"multi_select": [{"name": tag}]}
        }
    }
    
    cmd = [
        "curl.exe", "-s", "-X", "POST",
        "https://api.notion.com/v1/pages",
        "-H", f"Authorization: Bearer {NOTION_TOKEN}",
        "-H", "Notion-Version: 2022-06-28",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(body, ensure_ascii=False),
        "--connect-timeout", "60"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        response = json.loads(result.stdout)
        if response.get('object') == 'page':
            return True, response.get('id')
        else:
            return False, response.get('message', 'Unknown error')
    except Exception as e:
        return False, str(e)


def ima_append(content):
    """
    追加内容到IMA笔记
    
    重要：IMA API成功时返回 {"doc_id": "..."}，失败才返回code
    判断成功应检查 doc_id 字段是否存在
    
    参数:
        content: 要追加的内容（Markdown格式）
    
    返回:
        True 成功，False 失败
    """
    body = {
        "doc_id": IMA_NOTE_ID,
        "content_format": 1,  # 1表示Markdown格式
        "content": content
    }
    
    cmd = [
        "curl.exe", "-s", "-X", "POST",
        "https://ima.qq.com/openapi/note/v1/append_doc",
        "-H", "Content-Type: application/json",
        "-H", f"ima-openapi-clientid: {IMA_CLIENT_ID}",
        "-H", f"ima-openapi-apikey: {IMA_API_KEY}",
        "-d", json.dumps(body, ensure_ascii=False),
        "--connect-timeout", "60"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        response = json.loads(result.stdout)
        # 关键：检查doc_id字段而非code字段
        if response.get('doc_id'):
            return True
        else:
            print(f"IMA Error: {response.get('errmsg', response.get('message', 'Unknown error'))}")
            return False
    except Exception as e:
        print(f"IMA Error: {e}")
        return False


def build_md_content(updates):
    """构建Markdown内容"""
    md_content = f"# AI资讯更新 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += "**来源**: X（Twitter）和 Hacker News\n\n"
    md_content += "---\n\n"
    
    for i, update in enumerate(updates, 1):
        md_content += f"## {i}. {update['title']}\n\n"
        md_content += f"**来源**: {update['source']} | **日期**: {update['date']}\n\n"
        md_content += f"{update['summary']}\n\n"
        md_content += f"**链接**: [{update['url']}]({update['url']})\n\n"
        md_content += "---\n\n"
    
    return md_content


def save_to_obsidian(md_content):
    """保存到Obsidian本地"""
    filename = f"AI资讯_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    obsidian_file = os.path.join(OBSIDIAN_PATH, filename)
    try:
        with open(obsidian_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        return True, obsidian_file
    except Exception as e:
        return False, str(e)


def sync_to_notion(updates):
    """同步到Notion数据库"""
    success_count = 0
    failed_count = 0
    
    for i, update in enumerate(updates, 1):
        success, result = notion_add_page(
            title=update["title"],
            url=update["url"],
            summary=update["summary"],
            source=update["source"],
            date=update["date"]
        )
        
        if success:
            print(f"[OK] [{i}/{len(updates)}] 成功添加到 Notion: {update['title']}")
            success_count += 1
        else:
            print(f"[FAIL] [{i}/{len(updates)}] 添加失败: {update['title']}")
            print(f"     错误: {result}")
            failed_count += 1
        
        time.sleep(0.3)  # 避免API限流
    
    return success_count, failed_count


def sync_to_ima(md_content):
    """同步到IMA笔记"""
    success = ima_append("\n\n" + md_content)
    if success:
        print(f"[OK] 成功同步到 IMA 笔记 (笔记ID: {IMA_NOTE_ID})")
    else:
        print(f"[FAIL] 同步到 IMA 失败")
    return success


# ==================== 主程序 ====================

def main():
    # 检查运行模式
    mode = sys.argv[1] if len(sys.argv) > 1 else "full"
    
    print("=" * 80)
    print("AI资讯同步流程")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模式: {mode}")
    print("=" * 80)
    
    # 检查配置
    if "YOUR_" in NOTION_TOKEN or "YOUR_" in IMA_CLIENT_ID:
        print("\n[错误] 请先配置脚本顶部的凭证信息！")
        print("需要配置: NOTION_TOKEN, NOTION_DB_ID, IMA_CLIENT_ID, IMA_API_KEY, IMA_NOTE_ID, OBSIDIAN_PATH")
        return {"status": "error", "message": "Configuration required"}
    
    if not ai_updates:
        print("\n[警告] ai_updates 列表为空，请添加资讯数据或实现自动获取逻辑")
    
    if mode == "local":
        # 模式1：仅保存本地（定时任务第一阶段）
        print("\n[模式: 仅本地保存]")
        print("-" * 80)
        
        md_content = build_md_content(ai_updates)
        success, result = save_to_obsidian(md_content)
        
        if success:
            print(f"[OK] 成功保存到 Obsidian: {result}")
        else:
            print(f"[FAIL] 保存失败: {result}")
        
        return {"status": "local_only", "obsidian": success, "file": result if success else None}
    
    elif mode == "cloud":
        # 模式2：仅同步云端（定时任务第二阶段）
        print("\n[模式: 云端同步]")
        print("-" * 80)
        
        # 读取最新的本地文件
        files = sorted([f for f in os.listdir(OBSIDIAN_PATH) if f.startswith("AI资讯_")], reverse=True)
        if not files:
            print("[FAIL] 没有找到本地文件，请先执行 local 模式")
            return {"status": "error", "message": "No local file found"}
        
        latest_file = os.path.join(OBSIDIAN_PATH, files[0])
        print(f"读取本地文件: {latest_file}")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        print("\n[Step 1/2] 同步到 Notion 数据库...")
        print("-" * 80)
        notion_success, notion_failed = sync_to_notion(ai_updates)
        
        print("\n[Step 2/2] 同步到 IMA 笔记...")
        print("-" * 80)
        ima_success = sync_to_ima(md_content)
        
        return {
            "status": "success" if (notion_success > 0 and ima_success) else "partial",
            "notion": {"success": notion_success, "failed": notion_failed},
            "ima": ima_success,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    else:
        # 默认模式：完整执行
        print("\n[模式: 完整同步]")
        print("-" * 80)
        
        md_content = build_md_content(ai_updates)
        
        # Step 1: 保存到 Obsidian
        print("\n[Step 1/3] 保存到 Obsidian 本地...")
        print("-" * 80)
        obsidian_success, obsidian_file = save_to_obsidian(md_content)
        if obsidian_success:
            print(f"[OK] 成功保存到 Obsidian: {obsidian_file}")
        else:
            print(f"[FAIL] 保存失败: {obsidian_file}")
        
        # Step 2: 同步到 Notion 数据库
        print("\n[Step 2/3] 同步到 Notion 数据库...")
        print("-" * 80)
        notion_success, notion_failed = sync_to_notion(ai_updates)
        
        # Step 3: 同步到 IMA 笔记
        print("\n[Step 3/3] 同步到 IMA 笔记...")
        print("-" * 80)
        ima_success = sync_to_ima(md_content)
        
        # 最终报告
        print("\n" + "=" * 80)
        print("同步完成")
        print("=" * 80)
        print(f"Obsidian (本地):   {'[OK]' if obsidian_success else '[FAIL]'}")
        print(f"Notion (数据库):   {'[OK]' if notion_success > 0 else '[FAIL]'} ({notion_success}/{len(ai_updates)} 成功)")
        print(f"IMA (笔记):        {'[OK]' if ima_success else '[FAIL]'}")
        print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            "status": "success" if (obsidian_success and notion_success > 0 and ima_success) else "partial",
            "obsidian": obsidian_success,
            "notion": {"success": notion_success, "failed": notion_failed},
            "ima": ima_success,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "file": obsidian_file if obsidian_success else None
        }


if __name__ == "__main__":
    result = main()
    print(f"\n结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
