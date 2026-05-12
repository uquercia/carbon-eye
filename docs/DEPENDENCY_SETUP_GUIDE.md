# 碳眸项目依赖安装指南

本文档用于说明如何在本地把 `carbon-eye-campus` 项目的前端、后端和视觉相关依赖一次性安装到可运行状态。

## 1. 准备工作

### 1.1 安装基础环境

请先确认本机已经安装：

- **Python 3.10+**
- **Node.js 18+**
- **MySQL 8.0**
- **Git**

如果你已经有这些环境，可以直接进入下一步。

### 1.2 获取项目代码

把项目放到本地，例如：

```text
G:\codex\carbon-eye-campus
```

后续命令都以这个目录为例。

---

## 2. 安装后端依赖

后端使用的是 Python 虚拟环境 `.venv`，建议所有 Python 依赖都安装到这个环境里。

### 2.1 进入项目根目录

```powershell
cd G:\codex\carbon-eye-campus
```

### 2.2 创建并激活虚拟环境（如果还没有）

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

如果你已经有 `.venv`，可以直接激活它。

### 2.3 升级 pip

```powershell
python -m pip install --upgrade pip
```

### 2.4 安装核心依赖

先安装项目核心后端依赖：

```powershell
pip install -r requirements.txt
```

如果你想分开安装，也可以按模块安装：

```powershell
pip install -r requirements-core.txt
pip install -r requirements-vision.txt
```

### 2.5 依赖的作用

- **requirements-core.txt**
  - FastAPI
  - SQLAlchemy
  - PyMySQL
  - 数据库和接口基础依赖

- **requirements-vision.txt**
  - OpenCV
  - Pillow
  - PyTorch
  - Ultralytics YOLO
  - 图像处理和模型推理相关依赖

### 2.6 常见验证命令

安装完成后可以检查：

```powershell
python -c "import fastapi, sqlalchemy, pymysql; print('backend ok')"
```

如果没有报错，说明后端基础依赖已经装好。

---

## 3. 安装前端依赖

前端位于 `apps/web`，使用 Vite + Vue 3。

### 3.1 进入前端目录

```powershell
cd G:\codex\carbon-eye-campus\apps\web
```

### 3.2 安装 npm 依赖

由于本机 PowerShell 里容易拦截 `npm.ps1`，项目里统一用 `npm.cmd`：

```powershell
npm.cmd install
```

### 3.3 前端依赖安装完成后可以验证

```powershell
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

如果浏览器能打开页面，说明前端依赖正常。

---

## 4. 安装 Playwright 浏览器依赖

项目里如果需要跑浏览器自动化或截图验证，可以额外安装 Playwright 的 Chromium。

### 4.1 安装浏览器

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

### 4.2 说明

- 这一步只在你要做浏览器自动化、截图或回归测试时需要。
- 如果只是本地开发前后端页面，不一定必须安装。

---

## 5. 后端数据库相关准备

依赖安装完后，还要准备数据库配置。

### 5.1 复制环境文件

```powershell
copy apps\api\.env.example apps\api\.env
```

### 5.2 修改数据库连接

打开 `apps/api/.env`，修改：

- `DATABASE_URL`
- `MYSQL_ROOT_PASSWORD`

例如：

```env
DATABASE_URL=mysql+pymysql://root:你的MySQL密码@127.0.0.1:3306/carbon_eye?charset=utf8mb4
MYSQL_ROOT_PASSWORD=你的MySQL密码
```

### 5.3 初始化数据库

```powershell
cd G:\codex\carbon-eye-campus
.\.venv\Scripts\python.exe apps\api\scripts\init_db.py
```

---

## 6. 依赖安装顺序建议

建议按这个顺序来：

1. 安装 Python
2. 安装 Node.js
3. 安装 MySQL
4. 创建并激活 `.venv`
5. `pip install -r requirements.txt`
6. `cd apps/web && npm.cmd install`
7. 复制并修改 `apps/api/.env`
8. 初始化数据库
9. 启动后端
10. 启动前端

---

## 7. 启动命令汇总

### 7.1 启动后端

```powershell
cd G:\codex\carbon-eye-campus
.\.venv\Scripts\python.exe -m uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 7.2 启动前端

```powershell
cd G:\codex\carbon-eye-campus\apps\web
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

### 7.3 接口文档

- Swagger: `http://127.0.0.1:8000/docs`
- API 文档: `docs/API.md`

---

## 8. 常见问题

### 8.1 `npm.ps1` 被拦截怎么办？

改用：

```powershell
npm.cmd install
```

### 8.2 `.vue` 找不到类型声明怎么办？

确认 `apps/web/src/env.d.ts` 已存在。

### 8.3 MySQL 连接失败怎么办？

检查：

- MySQL 服务是否启动
- 用户名和密码是否正确
- 数据库 `carbon_eye` 是否已创建
- `.env` 里的 `DATABASE_URL` 是否正确

### 8.4 Python 包安装失败怎么办？

优先检查：

- 你是否真的激活了 `.venv`
- `pip` 是否已经升级
- 网络是否正常
- Python 版本是否兼容当前依赖

---

## 9. 这份文档的用途

这份文档的目标不是解释业务，而是让你明确：

- 要装哪些依赖
- 依赖装到哪里
- 先后顺序是什么
- 每一步成功后怎么验证

如果你以后需要，我还可以继续补一篇：

- **后端部署步骤文档**
- **前后端联调文档**
- **火山方舟视觉模型接入文档**
