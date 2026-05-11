# 碳眸后续待办与图片上传方案

## 当前未完成事项

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 校园图片上传按钮 | 未接入 | 前端已有上传区域，但还没有真正选择文件、上传到后端。 |
| 图片存储 | 未接入 | 需要决定本地存储还是对象存储。 |
| 动作/行为识别模型 | 未接入 | 当前页面只展示训练结果图和环保提示，还没有真实推理。 |
| 位置识别 | 未接入 | 当前楼栋位置是示意坐标，上传图片后还不能自动判断楼栋/地点。 |
| 识别任务表 | 未完整 | 目前有 `recognition_samples` 样例表，后续需要增加真实任务状态字段。 |
| 上传后行为影响分析 | 未接入 | 现在先留空，等图片识别完成后再生成行为影响。 |
| 训练数据管理 | 未接入 | 后续需要管理训练图片、标注结果、模型版本。 |
| 权限与登录 | 未接入 | 当前没有用户系统，适合演示，不适合正式部署。 |

## 图片上传后的推荐流程

1. 前端选择校园图片。
2. 前端调用后端上传接口，例如 `POST /api/uploads/images`。
3. 后端校验文件类型、大小。
4. 后端把图片保存到存储系统。
5. 后端在数据库保存图片 URL、上传时间、任务状态。
6. 后端创建识别任务，状态为 `pending`。
7. 模型服务读取图片，执行行为识别和位置识别。
8. 模型输出行为、位置、置信度、影响分析。
9. 后端把识别结果写入数据库。
10. 前端轮询任务详情或用 WebSocket 获取结果。

## 图片存储方案选择

### 方案 A：本地文件存储

做法：

- 图片保存到后端本地目录，例如 `apps/api/storage/uploads`。
- 数据库只保存相对 URL，例如 `/uploads/2026/05/xxx.jpg`。
- FastAPI 暴露静态文件访问路径。

优点：

- 开发最快。
- 不需要云服务账号。
- 适合大创演示、课程答辩、单机部署。

缺点：

- 多机器部署不方便。
- 图片备份、迁移、访问权限需要自己处理。
- 正式上线不够稳。

当前建议：第一阶段先用本地文件存储。

本项目当前已接入本地存储：

- 上传接口：`POST /api/uploads/images`
- 保存目录：`apps/api/storage/uploads`
- 访问地址：`http://127.0.0.1:8000/uploads/文件名`
- 数据库表：`uploaded_images`

### 方案 B：阿里云 OSS

做法：

- 后端接收图片后上传到阿里云 OSS。
- 数据库保存 OSS URL 或 object key。
- 前端通过后端返回的 URL 展示图片。

优点：

- 更适合正式部署。
- 图片访问速度、可靠性、扩展性更好。
- 后端服务器不用长期存大量图片。

缺点：

- 需要阿里云账号、Bucket、AccessKey、权限配置。
- 要处理签名 URL、公开读/私有读策略。
- 开发复杂度比本地存储高。

正式建议：

- 数据库不要存图片二进制。
- 数据库存 `object_key`、`public_url`、`content_type`、`file_size`、`created_at`。
- 如果图片涉及隐私，Bucket 用私有读，前端通过后端获取临时签名 URL。

结论：

- 大创演示、单机运行：本地存储更合适，简单、稳定、少配置。
- 真正上线、多用户访问：对象存储更合适，图片不占服务器磁盘，访问也更稳。
- 无论选哪种，数据库都不建议直接存图片二进制，只存 URL 或 object key。

## 视觉大模型选择

### 豆包/火山方舟

可以用。火山方舟官方文档里有“图片理解”能力，适合做校园图片中的行为描述、场景理解和结构化输出。项目后端已经按 OpenAI 兼容方式预留了配置：

```env
VISION_PROVIDER=ark
VISION_API_KEY=你的火山方舟APIKey
VISION_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VISION_MODEL=你的视觉模型接入点ID
```

注意：火山方舟里通常不是直接填“豆包”两个字，而是填你创建的模型接入点 ID。

### 阿里云百炼 Qwen-VL

也适合。阿里百炼官方视觉理解文档显示 Qwen-VL 支持图片描述、视觉问答、物体定位、视频理解等能力，并提供 OpenAI 兼容调用方式。

配置示例：

```env
VISION_PROVIDER=qwen
VISION_API_KEY=你的百炼APIKey
VISION_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
VISION_MODEL=qwen3.6-plus
```

### 当前建议

优先选豆包/火山方舟，如果你已经更熟悉字节系控制台；否则选阿里百炼 Qwen-VL，因为文档对图片/视频理解示例比较完整。

当前项目已经完成“可配置接入”，你拿到 API Key 和模型接入点后，只需要填 `.env` 并重启后端。

## 推荐落地路线

### 第一阶段：本地上传闭环

- 已增加 `uploaded_images` 表。
- 已增加 `recognition_tasks` 表。
- 已实现 `POST /api/uploads/images`。
- 已将图片保存到本地 `apps/api/storage/uploads`。
- 已在数据库保存图片 URL。
- 已实现前端上传后显示图片预览。

### 第二阶段：模拟识别结果

- 上传后先用规则或固定样例生成识别结果。
- 前端展示：
  - 行为 1：随手关灯关空调
  - 行为 2：及时关闭水龙头
  - 位置：教学楼/公共洗手区等
  - 置信度
  - 对用电/用水的估算影响

### 第三阶段：接入真实模型

- 已预留视觉大模型服务层。
- 后续可使用 YOLO 或自训练模型识别人、灯、水龙头、插座等目标。
- 对动作识别可以先做轻量方案：
  - 单张图：目标检测 + 场景规则。
  - 视频：抽帧 + 动作分类模型。
- 输出统一写入 `recognition_results` 表。

### 第四阶段：切换阿里云 OSS

- 封装 `StorageService`。
- 本地存储和 OSS 存储使用同一套接口。
- `.env` 配置决定使用 `local` 还是 `oss`。

## 建议新增数据库表

### `uploaded_images`

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `original_filename` | 原始文件名 |
| `storage_type` | `local` 或 `oss` |
| `object_key` | 本地路径或 OSS object key |
| `public_url` | 前端可访问 URL |
| `content_type` | 文件类型 |
| `file_size` | 文件大小 |
| `created_at` | 上传时间 |

### `recognition_tasks`

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `image_id` | 关联上传图片 |
| `status` | `pending/running/succeeded/failed` |
| `error_message` | 失败原因 |
| `created_at` | 创建时间 |
| `finished_at` | 完成时间 |

### `recognition_results`

| 字段 | 说明 |
| --- | --- |
| `id` | 主键 |
| `task_id` | 关联识别任务 |
| `behavior_name` | 行为名称 |
| `location_name` | 位置名称 |
| `confidence` | 置信度 |
| `electricity_delta_kwh` | 用电影响 |
| `water_delta_m3` | 用水影响 |
| `impact_summary` | 影响说明 |

## 下一步建议

下一次开发优先做：

1. 前端上传按钮可点击并选择图片。
2. 后端实现本地图片上传接口。
3. MySQL 增加 `uploaded_images` 和 `recognition_tasks`。
4. 前端上传后显示图片预览。
5. 上传完成后先返回模拟识别结果，跑通页面闭环。
