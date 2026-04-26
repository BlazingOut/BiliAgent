from duckduckgo_search import DDGS
from openai import OpenAI
from pydantic import BaseModel, Field
import json


# 定义大模型裁判的输出格式
class FactCheckResult(BaseModel):
    verdict: str = Field(description="判定结果：'完全真实', '部分真实', '存在误导', 或 '无法查证'")
    analysis: str = Field(description="结合搜索到的资料，给出 50 字左右的精简核查分析")
    reference_url: str = Field(description="支撑该判定的最佳参考网页链接（如果没有则填无）")

def search_news(insight_text):


def run_fact_check(insight_text: str, api_key: str, base_url: str) -> dict:
    """
    时政核验 Agent 的核心逻辑
    """
    print(f"🔍 Agent 正在全网搜索核验: {insight_text[:20]}...")

    # 1. 使用 DDG 搜索相关新闻 (获取前 3 条作为证据)
    search_results = ""
    best_url = "无"
    try:
        # 使用鸭鸭杀引擎搜索，限制结果数量
        results = DDGS().text(insight_text, max_results=3)
        for idx, res in enumerate(results):
            search_results += f"[信源 {idx + 1}]: {res['body']}\n链接: {res['href']}\n\n"
            if idx == 0:
                best_url = res['href']
    except Exception as e:
        search_results = "搜索失败或超时。"

    # 2. 呼叫大模型进行交叉验证
    client = OpenAI(api_key=api_key, base_url=base_url)

    schema_str = json.dumps(FactCheckResult.model_json_schema(), ensure_ascii=False)

    prompt = f"""
    你是一个严谨的事实核查专家。
    【待核查的观点】：{insight_text}
    【全网搜索到的最新资料】：
    {search_results}

    请对比资料，判断观点的真实性。不要带有个人政治立场，仅以搜索到的事实为准。
    必须严格按照以下 JSON Schema 输出格式：\n{schema_str}
    """

    print("🧠 大模型裁判正在比对证据...")
    response = client.chat.completions.create(
        model="deepseek-chat",  # 替换为你的模型
        messages=[
            {"role": "system", "content": "你是一个客观的事实核查员，严格输出 JSON 对象。"},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.1  # 核验需要极低的温度，保证严谨
    )

    result_str = response.choices[0].message.content.strip()
    if result_str.startswith("```json"):
        result_str = result_str[7:-3].strip()

    final_result = json.loads(result_str)
    # 如果大模型没有返回链接，我们把搜索到的第一个链接补给它
    if final_result.get("reference_url") in ["无", "", None] and best_url != "无":
        final_result["reference_url"] = best_url

    return final_result


# 🧪 测试一下
if __name__ == "__main__":
    test_claim = "匈牙利通胀率连续两年欧盟第一，食品价格四年涨81.6%"
    # 记得填入你的 Key
    res = run_fact_check(test_claim, api_key="你的_API_KEY",
                         base_url="[https://api.deepseek.com](https://api.deepseek.com)")
    print(json.dumps(res, indent=4, ensure_ascii=False))