import sqlite3
import json
import os

# 数据库文件会直接生成在你的项目目录里
DB_PATH = "agent_memory.db"


def init_db():
    """初始化数据库表结构 (Agent 的长期记忆分区)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 视频主表 (存储元数据和 LLM 总结)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            bvid TEXT PRIMARY KEY,       -- B站的BV号作为唯一主键
            title TEXT,                  -- 视频标题
            author TEXT,                 -- UP主
            b站分类 TEXT,                -- B站原生的分区标签
            summary TEXT,                -- 大模型提炼的一句话总结
            llm_category TEXT,           -- 大模型打的分类标签 (如 时政/健身)
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 存入时间
        )
    ''')

    # 2. 深度洞察表 (存储拆解出的 Key Insights)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bvid TEXT,                   -- 关联的视频ID
            content TEXT,                -- 具体的知识点内容
            FOREIGN KEY (bvid) REFERENCES videos(bvid)
        )
    ''')

    # 3. 行动清单表 (存储 Action Items)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bvid TEXT,
            action_text TEXT,            -- 行动指令
            is_completed BOOLEAN DEFAULT 0, -- 是否完成 (0=未完成, 1=已完成)
            FOREIGN KEY (bvid) REFERENCES videos(bvid)
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ 数据库表结构初始化成功！")


def save_video_meta(video_meta: dict):
    """单独保存视频的基础 Meta 数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 提取需要的字段，注意处理 B站 分类列表
    bvid = video_meta.get("bvid", "未知BV号")
    title = video_meta.get("title", "未知标题")
    author = video_meta.get("author", "未知作者")
    b站分类 = json.dumps(video_meta.get("category", []), ensure_ascii=False)

    # INSERT OR IGNORE: 如果这个 bvid 已经存在，就不重复插入了
    cursor.execute('''
        INSERT OR IGNORE INTO videos (bvid, title, author, b站分类)
        VALUES (?, ?, ?, ?)
    ''', (bvid, title, author, b站分类))

    conn.commit()
    conn.close()
    print(f"💾 视频基础信息已落库: [{title}]")


# 🧪 测试运行
if __name__ == "__main__":
    # 1. 创建数据库和表
    init_db()

    # 2. 模拟我们刚才从 yt-dlp 抓取到的 B 站原生数据
    mock_meta = {
        "bvid": "BV1zFouBYEZR",
        "title": "匈牙利人为什么非要抛弃欧尔班？",
        "author": "幼子",
        "category": ["知识", "校园学习"]
    }

    # 3. 存入数据库
    save_video_meta(mock_meta)