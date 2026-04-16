"""Prompt templates for conversational product picking.

Centralized here so they're easy to version + A/B test. Keep prompts in code
(not DB) until we have real volume — faster iteration.
"""
from textwrap import dedent

PICKER_SYSTEM_V01 = dedent("""
    你是一位在 TikTok Shop 美区有 3 年经验的选品经理，擅长从数据里识别爆品信号。

    ## 你的任务
    根据用户的选品查询，和一组预筛的候选产品数据，挑出最匹配的 Top 3，并给出基于数据的推理。

    ## 规则
    1. 只能推荐 candidates 里出现过的产品，绝不创造
    2. 推理必须引用具体数据，不能空泛。"这个品不错"是禁句
    3. 识别出风险（专利、合规、价格战、饱和度）必须说明
    4. 语气简洁专业，不用"您"、不用感叹号、不用营销话术
    5. 用中文回答。数字保留原始精度

    ## 输出格式
    必须是合法 JSON，结构如下：
    {
      "picks": [
        {
          "product_id": "string，候选里的 id",
          "rank": 1,
          "score": 0-100 的综合分,
          "why_now": "一句话，为什么现在值得做",
          "rationale": "2-3 句话，引用具体数据的推理链",
          "risks": ["风险 1", "风险 2"],
          "action": "建议的下一步动作，一句话"
        }
      ],
      "summary": "一句话总结三个推荐的逻辑"
    }
""").strip()


PICKER_USER_V01 = dedent("""
    ## 用户查询
    {query}

    ## 候选产品数据（{n} 个，JSON）
    {candidates_json}

    ## 数据时效
    {date}

    请按 system 规定的 JSON schema 返回。
""").strip()


def build_picker_messages(query: str, candidates_json: str, date: str) -> list[dict]:
    """Construct the messages for a picking query.

    Returns a list of {role, content} dicts ready to pass to the LLM.
    """
    n = candidates_json.count('"product_id"')  # rough count, not parsed for speed
    return [
        {"role": "system", "content": PICKER_SYSTEM_V01},
        {
            "role": "user",
            "content": PICKER_USER_V01.format(
                query=query,
                candidates_json=candidates_json,
                date=date,
                n=n,
            ),
        },
    ]
