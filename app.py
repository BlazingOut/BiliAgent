import streamlit as st
import json
import sqlite3

# 假设这是你之前写好的模块
from download_bz import download_bilibili_audio, audio_to_text
from llm import extract_video_info

import re


def extract_bvid(url):
    # 匹配 BV 开头的 12 位字母数字组合
    pattern = r'BV[a-zA-Z0-9]{10}'
    match = re.search(pattern, url)

    if match:
        return match.group(0)
    return None

def form_initial_prompt(video_meta: dict):
    # 🌟 核心：动态组装 initial_prompt
    dynamic_prompt = "这是一段中文视频，发音清晰，包含以下专有名词和语境："
    if video_meta:
        title = video_meta.get("title", "")
        author = video_meta.get("author", "")
        # B站的 tags 是一个列表，我们把它转成逗号分隔的字符串
        tags_str = "，".join(video_meta.get("tags", [])[:10])  # 保留前10个核心标签防超长

        # 组装高浓度小抄
        dynamic_prompt += f"标题《{title}》，UP主：{author}。核心关键词：{tags_str}。"
    return dynamic_prompt


def start_app():
    # 页面配置
    st.set_page_config(page_title="AI 内容沉淀 Agent", page_icon="🧠", layout="wide")

    st.title("🧠 AI Content Curation Agent")
    st.markdown("把碎片化的 B 站视频，转化为你的结构化第二大脑。")

    # --- 1. 左侧栏：历史记录区 ---
    with st.sidebar:
        st.header("🗂️ 我的知识库")
        # 这里未来可以写一个数据库查询，把看过的视频列出来
        st.write("✅ [时政] 2026匈牙利大选分析")
        st.write("✅ [健身] 居家背部训练指南")

    # --- 2. 主干区：处理新视频 ---
    bvid = st.text_input("🔗 输入 B 站视频链接 (例如: BV1zFouBYEZR)：")

    # 提取url中的bvid
    if "http" in bvid:
        bvid = extract_bvid(bvid)

    if st.button("🚀 开始沉淀知识", type="primary"):
        if bvid:
            with st.status("Agent 正在全力工作中...", expanded=True) as status:
                # 第一步
                st.write("📥 1. 正在绕过反爬抓取视频音频流...")
                meta_data, audio_path = download_bilibili_audio(bvid)
                context_prompt = form_initial_prompt(meta_data)
                # 第二步
                st.write("🗣️ 2. 唤醒 Whisper 进行语音转文本...")
                transcript = audio_to_text(audio_path, context_prompt)

                # 第三步
                st.write("🧠 3. 大模型深度思考，提取结构化知识...")
                knowledge_json = extract_video_info(transcript)

                status.update(label="✅ 处理完成！", state="complete", expanded=False)

            # --- 3. 展示结果 ---
            # 假设这是大模型返回的结果

            mock_data = knowledge_json

            st.success("✨ 提取成功！已自动存入数据库。")

            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("📝 核心总结")
                st.info(mock_data["summary"])

                st.subheader("💡 深度洞察")
                for idx, insight in enumerate(mock_data["key_insights"]):
                    st.write(f"{idx + 1}. {insight}")

            with col2:
                st.subheader("🏷️ 标签分类")
                st.button(mock_data["category"])

                st.subheader("🎯 行动清单")
                if mock_data["action_items"]:
                    for action in mock_data["action_items"]:
                        st.checkbox(action)  # 用 checkbox 更有待办事项的感觉
                else:
                    st.write("😴 纯知识输入，无需具体行动。")

        else:
            st.warning("请先输入视频链接哦！")


start_app()