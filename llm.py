from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
import json
API_KEY = "sk-638fc19f91d54d08bced3fd119c0d5e4"

class VideoKnowledge(BaseModel):
    summary: str = Field(description="用通俗易懂的话，一句话总结这个视频的核心观点")
    category: str = Field(description="为视频打上一个分类标签，例如：时政、AI、健身、学习方法等")
    key_insights: List[str] = Field(description="提取视频中的 3 到 5 个核心知识点或论据")
    action_items: List[str] = Field(description="如果视频中有具体的行动建议（如教程），提取为待办清单。如果是纯时政分析无具体行动，则返回空列表")


def extract_video_info(transcript: str) -> dict:
    client = OpenAI(
        api_key=API_KEY,  # 记得填入你的 Key
        base_url="https://api.deepseek.com"  # 或者你正在用的其他平台 URL
    )

    print("🧠 Agent 正在思考并提取结构化知识...")

    # 🌟 修复 1：动态获取 Pydantic 的 Schema 并转成字符串
    schema_str = json.dumps(VideoKnowledge.model_json_schema(), ensure_ascii=False)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                # 🌟 修复 2：在 System Prompt 中把 Schema 喂给大模型，并严厉警告它只能输出 JSON
                "content": (
                    "你是一个专业的知识沉淀与提炼助手。"
                    "你必须严格按照以下 JSON Schema 的格式输出结果，不要包含任何 Markdown 标记（如 ```json），"
                    f"直接输出纯 JSON 字符串！\n\n数据结构要求：\n{schema_str}"
                )
            },
            {"role": "user", "content": f"以下是视频转录文本：\n\n{transcript}"}
        ],
        # 🌟 修复 3：退回到所有模型都支持的 json_object 模式
        response_format={"type": "json_object"},
        temperature=0.3
    )

    result_str = response.choices[0].message.content

    # 因为有些模型就算开了 json_object，偶尔还是会带上 ```json 前缀，所以加一层容错清理
    result_str = result_str.strip()
    if result_str.startswith("```json"):
        result_str = result_str[7:-3].strip()

    return json.loads(result_str)


# 🧪 测试运行
if __name__ == "__main__":
    # 把你刚才识别出来的那段长长的文字放进来

    with open("./text/BV1zFouBYEZR.txt", 'r', encoding="utf-8") as f:
        transcript = f.read()

    result = extract_video_info(transcript)
    #
    # # 漂亮地打印出来看看效果
    save_dir = "./text/BV1zFouBYEZR_extract.json"
    with open(save_dir, 'w', encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    print(json.dumps(result, indent=4, ensure_ascii=False))