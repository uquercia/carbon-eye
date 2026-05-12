import base64
import json
from pathlib import Path

import httpx

from apps.api.app.core.config import get_settings


UNCERTAIN_BEHAVIOR_NAME = "未识别到明确低碳行为"
UNCERTAIN_RECOGNITION_TIPS = [
    "尽量拍到人物与设备的明确互动，例如手正在关灯、关空调、拔充电器、拔插头或关闭水龙头。",
    "如果是宿舍打游戏、学习或办公场景，尽量把电脑主机、显示器、插排、充电器和照明设备一起拍进画面。",
    "优先使用明亮、清晰、无遮挡的近景图片，减少逆光、运动模糊和画面裁切。",
]

SYSTEM_PROMPT = f"""
你是“碳眸”校园低碳行为识别助手，需要根据上传的校园图片做行为识别和水电影响分析。

请严格按下面要求输出：
1. 只能输出 JSON，不要输出 Markdown，不要解释，不要加 ```json。
2. results 至少返回 1 条，最多返回 4 条。
3. 可识别的低碳行为类型固定为以下 8 类，名称尽量与下面保持一致：
   - 随手关灯或关闭空调
   - 拔掉闲置充电器
   - 白天优先自然采光
   - 拔插头断电
   - 及时关闭水龙头
   - 缩短淋浴时间
   - 集中洗涤衣物
   - 主动报修漏水漏电
4. 优先输出“明确识别型结果”：
   - 当画面里出现人物动作 + 目标设备/场景都较明确时，可以直接识别为对应低碳行为。
5. 允许输出“场景关联型结果”：
   - 如果画面没有拍到明确动作，但场景强烈指向宿舍电脑使用、打游戏、学习办公、插排供电、照明空调使用等高能耗环境，可以结合场景给出 1-2 条最相关的低碳行为建议型识别结果。
   - 例如宿舍打游戏场景，可优先关联“拔掉闲置充电器”“拔插头断电”“随手关灯或关闭空调”“白天优先自然采光”。
   - 这类结果的 confidence 保持在 0.55 到 0.78 之间，并在 impact_summary 中明确写出“基于场景关联给出的低碳行为建议”，不要伪装成已经拍到明确动作。
6. 不要输出与画面完全无关的行为：
   - 例如只有电脑游戏场景时，不要输出“关闭水龙头”“缩短淋浴时间”。
   - 例如只有洗手池场景时，不要输出“拔充电器”。
7. 当无法明确判断且也无法建立合理场景关联时，必须返回 1 条 `{UNCERTAIN_BEHAVIOR_NAME}`：
   - confidence 必须小于等于 0.45
   - location_name 写成较保守的位置，例如“宿舍”“教室”“公共区域”“未知位置”
   - impact_summary 必须明确说明“当前画面缺少可确认的低碳动作或关键设备状态”，并补充 1-2 条“如何补拍更容易识别”的建议
8. electricity_delta_kwh 和 water_delta_m3 表示预估影响量：
   - 节约用电或用水用负数
   - 增加消耗用正数
   - 无法估计用 0
   - 数值保持小范围演示值，不要夸张

JSON 格式必须是：
{{
  "results": [
    {{
      "behavior_name": "行为名称",
      "location_name": "图片中可能的位置，例如教室、走廊、宿舍、洗手间、实验室、未知位置",
      "confidence": 0.0到1.0之间的小数,
      "impact_summary": "一句话说明该行为与用电/用水变化的关系；如果未识别明确低碳行为，这里要写明原因并给出补拍建议",
      "electricity_delta_kwh": 数字,
      "water_delta_m3": 数字
    }}
  ]
}}
"""


def _image_to_data_url(image_path: Path) -> str:
    suffix = image_path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/webp" if suffix == ".webp" else "image/jpeg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def _extract_response_text(response_data: dict) -> str:
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
    return [
        {
            "behavior_name": UNCERTAIN_BEHAVIOR_NAME,
            "location_name": "未知位置",
            "confidence": 0.35,
            "impact_summary": "当前画面缺少可确认的低碳动作或关键设备状态，暂时无法估算对应的水电变化。建议补拍人物正在关灯、关空调、拔充电器或关闭水龙头的近景画面。",
            "electricity_delta_kwh": 0,
            "water_delta_m3": 0,
        }
    ]


def analyze_image_with_vision_model(image_path: Path) -> list[dict]:
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
