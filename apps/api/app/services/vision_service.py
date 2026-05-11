import base64
import json
from pathlib import Path

import httpx

from apps.api.app.core.config import get_settings


SYSTEM_PROMPT = """
你是“碳眸”校园低碳行为识别助手，需要根据上传的校园图片做行为识别和水电影响分析。

请严格按下面要求输出：
1. 只输出 JSON，不要输出 Markdown，不要解释，不要加 ```json。
2. results 至少返回 1 条，最多返回 4 条。
3. 如果图片里能判断出行为，请优先识别这些类型：
   - 随手关灯或关闭空调
   - 拔掉闲置充电器
   - 白天优先自然采光
   - 及时关闭水龙头
   - 缩短淋浴时间
   - 集中洗涤衣物
   - 主动报修漏水漏电
4. 如果图片无法明确判断低碳行为，也不要返回空数组；请返回 1 条“未识别到明确低碳行为”，并给出适合展示在汇报大屏上的说明。
5. electricity_delta_kwh 和 water_delta_m3 表示预估影响量：
   - 节约用电或节约用水用负数；
   - 增加消耗用正数；
   - 无法估计用 0；
   - 数字保持小范围演示值，不要夸张。

JSON 格式必须是：
{
  "results": [
    {
      "behavior_name": "行为名称",
      "location_name": "图片中可能的位置，例如教室、走廊、宿舍、洗手间、实验室、未知位置",
      "confidence": 0.0到1.0之间的小数,
      "impact_summary": "一句话说明该行为与用电/用水变化的关系，适合前端直接展示",
      "electricity_delta_kwh": 数字,
      "water_delta_m3": 数字
    }
  ]
}
"""


def _image_to_data_url(image_path: Path) -> str:
    """把本地图片转成 data URL，便于直接传给火山方舟 Responses API。"""

    suffix = image_path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/webp" if suffix == ".webp" else "image/jpeg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def _extract_response_text(response_data: dict) -> str:
    """从火山方舟 Responses API 返回体中提取文本。

    不同模型/版本返回结构可能略有差异，所以这里做得宽松一点：
    优先读 output_text；如果没有，再从 output/content 里找文本。
    """

    if response_data.get("output_text"):
      return str(response_data["output_text"])

    chunks: list[str] = []
    for output_item in response_data.get("output", []):
        for content_item in output_item.get("content", []):
            text = content_item.get("text")
            if text:
                chunks.append(str(text))
    return "\n".join(chunks)


def _parse_model_json(text: str) -> dict:
    """把模型返回的文本解析成 JSON。

    视觉大模型偶尔会把 JSON 包在 ```json 代码块里，或者在 JSON 前后补一句话。
    为了让接口更稳，这里会先尝试直接解析；失败后再截取第一个 { 到最后一个 }。
    """

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(cleaned[start : end + 1])


def _fallback_uncertain_result() -> list[dict]:
    """模型没有返回结果时使用的兜底分析。

    前端上传图片后需要看到“分析结果”，即使模型认为图片不够清晰，
    也应该给出一个可读的待确认结论，而不是让页面空白。
    """

    return [
        {
            "behavior_name": "未识别到明确低碳行为",
            "location_name": "未知位置",
            "confidence": 0.32,
            "impact_summary": "当前图片没有足够清晰的动作或设备状态，建议补充包含灯光、空调、水龙头或充电设备的场景图后再分析。",
            "electricity_delta_kwh": 0,
            "water_delta_m3": 0,
        }
    ]


def analyze_image_with_vision_model(image_path: Path) -> list[dict]:
    """调用豆包/火山方舟 Responses API 分析图片。

    本项目按你给的 curl 示例接入：
    POST https://ark.cn-beijing.volces.com/api/v3/responses
    content 类型使用 input_image + input_text。
    """

    settings = get_settings()
    if not settings.vision_api_key or not settings.vision_model:
        return []

    endpoint = f"{settings.vision_base_url.rstrip('/')}/responses"
    payload = {
        "model": settings.vision_model,
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "image_url": _image_to_data_url(image_path)},
                    {"type": "input_text", "text": SYSTEM_PROMPT},
                ],
            }
        ],
    }

    with httpx.Client(timeout=60) as client:
        response = client.post(
            endpoint,
            headers={
                "Authorization": f"Bearer {settings.vision_api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()

    text = _extract_response_text(response.json()) or "{}"
    data = _parse_model_json(text)
    results = data.get("results", [])
    return results or _fallback_uncertain_result()
