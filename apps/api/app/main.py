from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from apps.api.app.api.routes import router
from apps.api.app.core.config import get_settings

# FastAPI 应用对象。
# 你可以把它理解成“后端服务的入口文件”：
# - uvicorn 启动时会读取这里的 app
# - Swagger 文档里的标题、描述也来自这里
# - 路由、中间件都在这里注册
app = FastAPI(
    title="碳眸校园低碳驾驶舱 API",
    description="提供楼栋水电预测、低碳行为识别样例、训练结果图片等数据接口。",
    version="0.1.0",
)

# 跨域配置。
# 前端运行在 5173/4173 端口，后端运行在 8000 端口。
# 浏览器会认为它们是不同来源，所以必须允许这些前端地址访问 API。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 把 apps/api/app/api/routes.py 里定义的所有接口挂到 app 上。
app.include_router(router)

# 把本地上传目录挂成静态文件服务。
# 图片保存到 apps/api/storage/uploads 后，前端可以通过 /uploads/文件名 访问。
settings = get_settings()
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
