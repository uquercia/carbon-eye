# 碳眸 API 接口文档

后端服务地址：

```text
http://127.0.0.1:8000
```

Swagger 自动文档：

```text
http://127.0.0.1:8000/docs
```

## 1. 健康检查

```http
GET /api/health
```

用途：确认后端服务是否启动。

响应示例：

```json
{
  "status": "ok"
}
```

## 2. 获取驾驶舱全部数据

```http
GET /api/dashboard
```

用途：前端首页主要接口，一次性返回楼栋水电、趋势图、行为识别样例、行为影响规则、训练结果图片。

主要返回字段：

| 字段 | 说明 |
| --- | --- |
| `summary` | 顶部统计卡片数据 |
| `buildings` | 楼栋最新时间步水电预测数据 |
| `behavior_scores` | 各专业低碳行为得分 |
| `trends` | 按时间步汇总的水电趋势 |
| `recognition_samples` | 已识别行为样例 |
| `behavior_impacts` | 行为对用电/用水影响的规则说明 |
| `training_images` | 训练完成后的结果图 |

响应片段：

```json
{
  "summary": {
    "electricity_actual_total": 1135620.03125,
    "electricity_predicted_total": 1208911.6094,
    "water_actual_total": 1310903.179,
    "water_predicted_total": 1455452.301
  },
  "recognition_samples": [
    {
      "behavior_name": "随手关灯关空调",
      "location_name": "教学楼教室",
      "confidence": 0.93,
      "impact_summary": "识别到离开教室后关闭电器，预计降低化学大楼夜间空载用电。"
    }
  ]
}
```

## 3. 获取楼栋最新水电数据

```http
GET /api/buildings
```

用途：只获取右侧楼栋预测结果表和地图节点需要的数据。

字段说明：

| 字段 | 说明 |
| --- | --- |
| `id` | 楼栋 ID |
| `name` | 楼栋名称 |
| `zone` | 区域 |
| `major` | 专业/功能映射 |
| `electricity_actual` | 实际用电量 |
| `electricity_predicted` | 预测用电量 |
| `water_actual` | 实际用水量 |
| `water_predicted` | 预测用水量 |
| `map_x` / `map_y` | 前端示意地图坐标百分比 |

## 4. 获取水电趋势

```http
GET /api/trends
```

用途：底部用电、用水实际/预测趋势图。

## 5. 获取识别行为样例

```http
GET /api/recognition-samples
```

用途：红框 2 的“行为 1、行为 2...”列表。

字段说明：

| 字段 | 说明 |
| --- | --- |
| `behavior_name` | 识别出的低碳行为 |
| `location_name` | 识别位置 |
| `confidence` | 识别置信度 |
| `impact_summary` | 对用电/用水影响的文字说明 |
| `electricity_delta_kwh` | 估算用电影响 |
| `water_delta_m3` | 估算用水影响 |
| `image_url` | 关联训练结果图 |

## 6. 获取行为影响规则

```http
GET /api/behavior-impacts
```

用途：说明不同行为为什么会影响用电、用水。

例如：

- 随手关灯关空调：降低空载用电。
- 及时关闭水龙头：降低公共区域用水浪费。
- 主动报修漏水漏电：减少持续浪费。

## 7. 获取训练结果图片

```http
GET /api/training-images
```

用途：红框 1 的训练结果图片区。

当前图片来自 `G:\大创碳眸项目` 中已有训练/预测图，初始化脚本会复制到：

```text
apps/web/public/training
```

## 8. 上传校园图片

```http
POST /api/uploads/images
Content-Type: multipart/form-data
```

表单字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `file` | File | JPG、PNG、WEBP 图片 |

用途：

1. 保存校园图片到本地存储。
2. 在 `uploaded_images` 表保存图片 URL。
3. 创建 `recognition_tasks` 识别任务。
4. 如果 `.env` 已配置视觉大模型，则调用模型并写入 `recognition_results`。
5. 如果未配置模型，则返回等待配置状态。

响应示例：

```json
{
  "image": {
    "id": 1,
    "original_filename": "classroom.jpg",
    "public_url": "http://127.0.0.1:8000/uploads/xxx.jpg",
    "content_type": "image/jpeg",
    "file_size": 123456
  },
  "task": {
    "id": 1,
    "status": "pending_model_config",
    "model_provider": "none",
    "model_name": "",
    "error_message": "未配置视觉大模型 API Key，已完成图片保存，等待后续分析。"
  },
  "results": [],
  "message": "图片已上传，等待配置视觉大模型后分析。"
}
```

## 数据库表

| 表名 | 用途 |
| --- | --- |
| `buildings` | 楼栋基础信息和地图示意坐标 |
| `energy_predictions` | 楼栋用电/用水实际值、预测值和误差 |
| `behavior_scores` | 专业低碳行为问卷得分 |
| `recognition_samples` | 训练后/识别后行为样例 |
| `behavior_impacts` | 行为影响规则 |
| `training_images` | 训练结果图片 |
| `uploaded_images` | 用户上传的校园图片 URL 和元数据 |
| `recognition_tasks` | 图片识别任务状态 |
| `recognition_results` | 大模型或动作识别模型输出的行为结果 |

## 初始化数据库

先准备本地环境文件：

```powershell
copy apps\api\.env.example apps\api\.env
```

然后修改 `apps\api\.env` 中的 `DATABASE_URL` 和 `MYSQL_ROOT_PASSWORD`。

```powershell
cd G:\codex\carbon-eye-campus
.\.venv\Scripts\python.exe apps\api\scripts\init_db.py
```

## 启动后端

```powershell
cd G:\codex\carbon-eye-campus
.\.venv\Scripts\python.exe -m uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000
```
