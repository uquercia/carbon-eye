FROM docker.m.daocloud.io/library/python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=180 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 统一将容器工作目录放在 /app，后续源码复制和卷挂载都以这里为根目录。
WORKDIR /app

COPY requirements-core.txt ./requirements-core.txt

# 这里只安装后端运行时依赖，不在容器里重复做额外 pip install。
RUN pip install --upgrade pip \
    && pip install -r requirements-core.txt

COPY apps ./apps

# 上传文件实际会落到卷里，这里只确保目录存在。
RUN mkdir -p /app/apps/api/storage/uploads

EXPOSE 8000

CMD ["uvicorn", "apps.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
