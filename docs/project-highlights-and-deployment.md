# Carbon Eye Campus 项目说明

## 1. 需求来源与真实性边界

这份说明只基于当前仓库里的真实代码、配置和文档整理，不是凭空补写。当前主要依据如下：

- `README.md`
- `TECH_STACK.md`
- `apps/api/app/models/campus.py`
- `apps/api/scripts/init_db.py`
- `apps/api/app/api/routes.py`
- `apps/api/app/services/dashboard_service.py`
- `apps/web/src/features/dashboard/DashboardView.vue`
- `docs/API.md`

因此下面内容可以确认：

- 项目是一个“校园低碳行为 + 水电预测 + 可视化驾驶舱”的前后端一体演示系统。
- 后端已经接入 FastAPI、SQLAlchemy、MySQL 和图片上传入口。
- 前端已经接入仪表盘、楼栋地图、趋势图、行为图、训练结果图和上传入口。
- 目前既有真实数据库结构，也有“初始化样例数据”和“前端 fallback 数据”两套兜底机制。

## 2. 数据处理亮点

### 2.1 多源数据整合到统一驾驶舱

后端初始化脚本 `apps/api/scripts/init_db.py` 已把多类数据整合进统一库：

- `prediction_results.csv` 导入楼栋水电实际值、预测值和误差。
- `behavior_summary(1).csv` 导入专业维度的低碳行为问卷得分。
- 训练完成后的图片复制到 `apps/web/public/training`，同时写入 `training_images` 表。
- 上传图片后，文件元数据、识别任务、识别结果分别写入独立表，形成可扩展的任务链路。

### 2.2 原始数据与展示数据分层

项目没有把所有逻辑塞进前端，而是做了明确分层：

- 数据库存原始业务数据和任务数据。
- `dashboard_service.py` 负责聚合与汇总。
- `/api/dashboard` 一次性返回首页所需数据，降低前端多请求拼装成本。
- 前端把后端 `snake_case` 再转换成 `camelCase`，保证接口层与页面层职责清楚。

### 2.3 对“暂无真实模型结果”的处理比较稳

当前行为识别链路并不是硬伪造“已经识别成功”，而是分成三层：

- `recognition_samples`：初始化样例，用于没有真实上传时的演示。
- `behavior_impacts`：行为规则库，用于解释行为为什么会影响水电。
- `recognition_results`：真实上传图片后的结构化识别结果表，后续可被真实模型写入。

这意味着系统已经把“展示样例”和“真实识别结果”在数据结构上分开了，后续替换模型时不会推翻现有页面结构。

## 3. 技术处理亮点

### 3.1 后端是聚合型 API，不是散乱拼接口

首页核心走 `/api/dashboard` 聚合接口，能一次返回：

- summary
- buildings
- behavior_scores
- trends
- recognition_samples
- behavior_impacts
- training_images

这对答辩演示、弱网环境和前端加载稳定性都更合适。

### 3.2 数据模型已经为云端扩展留了口

现有表结构不是只够本地 demo：

- `uploaded_images` 支持 `storage_type`、`object_key`、`public_url`，可以从本地存储切到 OSS / COS / S3。
- `recognition_tasks` 支持任务状态、模型提供方、模型名、错误信息，方便异步化和多模型接入。
- `recognition_results` 独立建表，便于一张图识别多个行为结果。

### 3.3 前端对后端不可用有兜底

`DashboardView.vue` 在 API 不通时会回退到本地示例数据，避免大屏空白。这个机制适合演示，但正式部署时建议保留告警、弱化 fallback。

## 4. 当前已有接口

按 `apps/api/app/api/routes.py`，当前已有 8 个接口：

1. `GET /api/health`
   用途：健康检查。
2. `GET /api/dashboard`
   用途：首页聚合数据接口。
3. `GET /api/buildings`
   用途：楼栋最新水电数据。
4. `GET /api/trends`
   用途：水电趋势图数据。
5. `GET /api/recognition-samples`
   用途：获取识别行为样例。
6. `GET /api/behavior-impacts`
   用途：获取行为影响规则说明。
7. `GET /api/training-images`
   用途：获取训练结果图片。
8. `POST /api/uploads/images`
   用途：上传校园图片、落库、创建识别任务，并在有模型配置时返回识别结果。

补充：

- 详细字段说明继续看 `docs/API.md`。
- Swagger 地址是 `http://127.0.0.1:8000/docs`。

## 5. 数据库与部署说明

### 5.1 建库建表 SQL

- 已整理到 `docs/database-schema.sql`
- 该文件来源于当前 SQLAlchemy 模型和 `init_db.py` 的建库逻辑

### 5.2 本地部署步骤

1. 复制环境变量文件：

```powershell
copy apps\api\.env.example apps\api\.env
copy apps\web\.env.example apps\web\.env
```

2. 配置 MySQL：

- `DATABASE_URL`
- `MYSQL_ROOT_PASSWORD`
- `DATABASE_NAME=carbon_eye`

3. 初始化数据库：

```powershell
cd G:\codex\carbon-eye-campus
.\.venv\Scripts\python.exe apps\api\scripts\init_db.py
```

4. 启动后端：

```powershell
cd G:\codex\carbon-eye-campus
.\.venv\Scripts\python.exe -m uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000
```

5. 启动前端：

```powershell
cd G:\codex\carbon-eye-campus\apps\web
npm.cmd install
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

## 6. 云端部署前置工作

当前代码已经做好的前置基础：

- 前后端分离，适合分别部署。
- API 和前端地址都支持通过 `.env` 配置。
- 上传文件路径已抽成配置项。
- 图片元数据和任务状态已入库，具备服务化基础。

建议你在正式上云前优先确认这 6 项：

1. 数据库改为云 MySQL，并把 `DATABASE_URL` 指向云库。
2. `UPLOAD_DIR` 不再长期依赖本机磁盘，切换到对象存储。
3. `PUBLIC_UPLOAD_BASE_URL` 改成云域名或 CDN 域名。
4. `allow_origins` 从本地 5173/4173 扩成你的正式前端域名。
5. 视觉模型相关配置单独走环境变量，不写死在仓库。
6. 把初始化数据脚本和生产数据脚本分开，避免重置演示库。

## 7. 当前仍需注意的展示风险

- 行为识别结果链路已经有真实上传入口，但是否返回真实 AI 结果，取决于 `VISION_API_KEY` 和 `VISION_MODEL` 是否配置完成。
- 前端仍保留 fallback 示例数据机制，适合演示，不等于生产真实数据源。
- `recognition_samples` 和 `behavior_impacts` 本质上仍属于初始化演示数据，不应对外宣称为实时识别结果。
