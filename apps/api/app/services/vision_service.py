import base64
import json
from pathlib import Path

from openai import OpenAI

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
    """把本地图片转成 data URL，方便传给支持 OpenAI 兼容格式的视觉模型。"""

    suffix = image_path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/webp" if suffix == ".webp" else "image/jpeg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def analyze_image_with_vision_model(image_path: Path) -> list[dict]:
    """调用视觉大模型分析图片。

    当前按 OpenAI 兼容接口封装。
    豆包火山方舟、阿里百炼等平台都提供类似的 OpenAI 兼容调用方式，
    所以这里把 base_url、api_key、model 都放到 .env 里配置。
    """

    settings = get_settings()
    if not settings.vision_api_key or not settings.vision_model:
        return []

    client = OpenAI(api_key=settings.vision_api_key, base_url=settings.vision_base_url)
    completion = client.chat.completions.create(
        model=settings.vision_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": SYSTEM_PROMPT},
                    {"type": "image_url", "image_url": {"url": _image_to_data_url(image_path)}},
                ],
            }
        ],
        response_format={"type": "json_object"},
    )

    text = completion.choices[0].message.content or '{"results":[]}'
    data = json.loads(text)
    return data.get("results", [])
