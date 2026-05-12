# 碳眸校园低碳行为与水电预测平台

本项目面向中兴大学，目标是把学生低碳行为、楼栋水电数据、预测结果和可视化驾驶舱整合到一个系统中。当前阶段先完成前端驾驶舱页面，行为识别和位置识别接口暂不接入。

## 当前已完成

- 创建 `apps/web` 前端应用：Vue 3 + Vite + TypeScript。
- 创建 `apps/api` 后端应用：FastAPI + SQLAlchemy + MySQL。
- 搭建“碳眸”驾驶舱首页：
  - 顶部项目状态与 MySQL 本地连接提示。
  - 左侧图片/行为识别入口预留。
  - 中间中兴大学楼栋关系示意图。
  - 右侧楼栋用电、用水、预测值数据表。
  - 底部用电趋势、用水趋势、专业低碳行为得分图。
- 使用现有 CSV/图片资料整理了示例楼栋数据和统计数据。
- 创建 Python 虚拟环境和后端/算法依赖清单。
- 本地安装并验证 FastAPI、MySQL 驱动、OpenCV、PyTorch CPU、Ultralytics、Playwright。
- 已创建 `carbon_eye` 数据库，并导入楼栋水电预测、行为得分、识别样例、训练图片数据。
- 已接入校园图片上传，本地保存图片并在数据库保存 URL。

## 技术栈

前端：

- Vue 3
- Vite
- TypeScript
- Element Plus
- Apache ECharts
- lucide-vue-next

后端/算法规划：

- FastAPI
- SQLAlchemy + PyMySQL
- MySQL 8.0，本地数据库名建议 `carbon_eye`
- OpenCV + Pillow
- PyTorch
- Ultralytics YOLO

更完整的技术方案见 [TECH_STACK.md](./TECH_STACK.md)。

## 目录结构

```text
carbon-eye-campus/
  apps/
    web/                    # 前端驾驶舱应用
      src/
        features/dashboard/ # 碳眸驾驶舱业务模块
        shared/components/  # 通用组件
  ENVIRONMENT_STATUS.md     # 本机环境与依赖安装状态
  TECH_STACK.md             # 技术栈、需求理解、缺口清单
  requirements-core.txt     # Python 核心依赖
  requirements-vision.txt   # 视觉/深度学习依赖
  requirements.txt          # 合并依赖
```

## 运行前端

进入前端目录：

```powershell
cd G:\codex\carbon-eye-campus\apps\web
```

安装依赖：

```powershell
npm.cmd install
```

启动开发服务：

```powershell
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

或者预览构建结果：

```powershell
npm.cmd run build
npm.cmd run preview -- --host 127.0.0.1 --port 4173
```

当前预览地址：

```text
http://127.0.0.1:4173
```

说明：本机 PowerShell 会拦截 `npm.ps1`，所以命令里统一使用 `npm.cmd`。

## 运行后端

先创建本地配置文件，真实密码只放在 `.env`，不要提交到 git：

```powershell
copy apps\api\.env.example apps\api\.env
```

然后把 `apps\api\.env` 中的 `DATABASE_URL` 和 `MYSQL_ROOT_PASSWORD` 改成本机 MySQL 密码。

初始化数据库：

```powershell
cd G:\codex\carbon-eye-campus
.\.venv\Scripts\python.exe apps\api\scripts\init_db.py
```

启动接口服务：

```powershell
cd G:\codex\carbon-eye-campus
.\.venv\Scripts\python.exe -m uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000
```

接口文档：

```text
http://127.0.0.1:8000/docs
docs/API.md
```

## 一键启动前后端

如果你想像 Spring Boot 的 `Application` 一样只运行一个入口文件，可以直接执行根目录的启动脚本：

```powershell
cd G:\codex\carbon-eye-campus
python run_dev.py
```

它会先启动后端，再启动前端。

## 后续未完成任务

- 真实行为识别模型 API Key 还未配置，当前上传图片后会保存文件并创建识别任务。
- 动作识别还未训练专用模型，当前优先预留视觉大模型接口。
- 如果需要真实地图，可继续补中兴大学楼栋坐标；当前使用的是示意坐标。

## MySQL 信息

当前已知：

- 本地服务：`MySQL80`
- 地址：`127.0.0.1:3306`
- 数据库：允许创建 `carbon_eye`
- root 密码：写入本地 `apps/api/.env`，不要提交到 git。
