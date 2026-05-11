# 环境安装与连接状态

更新时间：2026-05-11

## 项目位置

项目目录：`G:\codex\carbon-eye-campus`

虚拟环境：`G:\codex\carbon-eye-campus\.venv`

## 已安装能力

| 能力 | 状态 |
| --- | --- |
| FastAPI 后端 | 已安装并导入验证通过 |
| MySQL Python 驱动 | `PyMySQL`、`mysql-connector-python` 已安装 |
| SQLAlchemy/Alembic | 已安装 |
| 数据处理 | pandas、numpy、scikit-learn、openpyxl 已安装 |
| 图表/原型绘图 | matplotlib 已安装 |
| 图像处理 | Pillow、OpenCV 已安装 |
| 深度学习 | PyTorch CPU 版、torchvision CPU 版已安装 |
| YOLO | Ultralytics 已安装 |
| 浏览器自动化 | Playwright 已安装 |

## 关键版本

| 包 | 版本 |
| --- | --- |
| fastapi | 0.136.1 |
| sqlalchemy | 2.0.49 |
| pandas | 3.0.2 |
| opencv-python | 4.13.0.92 |
| torch | 2.11.0+cpu |
| torchvision | 0.26.0+cpu |
| ultralytics | 8.4.48 |
| playwright | 1.59.0 |

## MySQL 状态

| 项目 | 状态 |
| --- | --- |
| MySQL 服务 | `MySQL80` 正在运行 |
| 本地端口 | `127.0.0.1:3306` 连通 |
| 账号密码 | 未配置，需要用户提供 |
| 建议数据库名 | `carbon_eye` |

后续连接字符串建议放入 `.env`：

```env
DATABASE_URL=mysql+pymysql://用户名:密码@127.0.0.1:3306/carbon_eye?charset=utf8mb4
```

## 浏览器状态

Playwright 安装浏览器时，`Chrome for Testing` 主体下载成功：

`C:\Users\MT\AppData\Local\ms-playwright\chromium-1217\chrome-win64\chrome.exe`

但 `Chrome Headless Shell` 额外包下载失败，错误是远端连接拒绝/重置。已用下载成功的 `chrome.exe` 做 Playwright 启动验证，结果通过。因此当前可以做前端截图验证；如以后需要完整 Playwright 浏览器包，可重新执行：

```powershell
& "G:\codex\carbon-eye-campus\.venv\Scripts\python.exe" -m playwright install chromium
```

## 已创建依赖文件

| 文件 | 用途 |
| --- | --- |
| `requirements-core.txt` | 后端、MySQL、数据处理、浏览器自动化核心依赖 |
| `requirements-vision.txt` | OpenCV、PyTorch、YOLO 视觉依赖 |
| `requirements.txt` | 合并依赖清单 |

## 下一步建议

1. 提供 MySQL 用户名、密码，或确认可以使用现有 root 账号创建 `carbon_eye`。
2. 补充 `用电用水数据.xlsx` 和 `questionnaire_results.xlsx` 原始数据文件。
3. 确认是否先做演示版识别：用 YOLO 通用模型识别人/物体，再把行为类别做成可人工标注或规则映射。
4. 开始搭建 FastAPI + MySQL 项目结构，并导入现有 CSV 数据。
