import base64
import json
from pathlib import Path

import httpx

from apps.api.app.core.config import get_settings


SYSTEM_PROMPT = """
你是校园低碳行为识别助手。请根据图片判断是否出现与节能、节水有关的行为。
只输出 JSON，不要输出多余解释。JSON 格式：
{
  "results": [
    {
      "behavior_name": "行为名称",
      "location_name": "图片中可能的位置",
      "confidence": 0.0到1.0,
      "impact_summary": "该行为对用电或用水的影响",
      "electricity_delta_kwh": 数字,
      "water_delta_m3": 数字
    }
  ]
}
如果图片无法判断行为，results 返回空数组。
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

    text = _extract_response_text(response.json()) or '{"results":[]}'
    data = json.loads(text)
    return data.get("results", [])
