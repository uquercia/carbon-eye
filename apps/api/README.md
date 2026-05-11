# 碳眸 API 后端

后端使用 FastAPI + SQLAlchemy + MySQL，负责从 `carbon_eye` 数据库读取楼栋、水电预测、低碳行为识别和训练结果数据。

## 初始化数据库

```powershell
cd G:\codex\carbon-eye-campus
.\.venv\Scripts\python.exe apps\api\scripts\init_db.py
```

## 启动接口服务

```powershell
cd G:\codex\carbon-eye-campus
.\.venv\Scripts\python.exe -m uvicorn apps.api.app.main:app --host 127.0.0.1 --port 8000 --reload
```

接口文档：

- Swagger: `http://127.0.0.1:8000/docs`
- 项目接口说明：`docs/API.md`
