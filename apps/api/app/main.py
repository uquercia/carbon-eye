from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.app.api.routes import router

app = FastAPI(
    title="碳眸校园低碳驾驶舱 API",
    description="提供楼栋水电预测、低碳行为识别样例、训练结果图片等数据接口。",
    version="0.1.0",
)

# 前后端分开运行时，浏览器会检查跨域权限。
# 这里允许本机 Vite 开发服务访问后端接口。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
