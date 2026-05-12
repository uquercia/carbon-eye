# 云端 Docker 部署说明

本文档只保留当前项目实际在用的一套部署方式：

- 本地修改代码
- 把代码同步到云服务器
- 在云服务器执行 `docker compose build` 和 `docker compose up -d`

不再使用“本地打镜像 tar 再上传”的旧方案。

## 1. 当前部署结构

云服务器上有 3 个容器：

- `carbon-eye-web`
  - 对外暴露 `80` 端口
  - 提供前端静态页面
  - 通过 `nginx.conf` 把 `/api`、`/uploads` 转发给后端
- `carbon-eye-api`
  - 运行 FastAPI
  - 只在 Docker 内网暴露 `8000`
- `carbon-eye-db`
  - 运行 MySQL 8.4
  - 只在 Docker 内网使用，不直接暴露公网端口

对应编排文件：

- [docker-compose.server-build.yml](/G:/codex/carbon-eye-campus/deploy/docker/docker-compose.server-build.yml)

## 2. 关键文件说明

- [api.Dockerfile](/G:/codex/carbon-eye-campus/deploy/docker/api.Dockerfile)
  - 构建后端镜像
  - 安装 Python 依赖
  - 启动 `uvicorn`
- [web.Dockerfile](/G:/codex/carbon-eye-campus/deploy/docker/web.Dockerfile)
  - 构建前端镜像
  - 执行 `npm install` 和 `npm run build`
  - 用 Nginx 托管构建产物
- [nginx.conf](/G:/codex/carbon-eye-campus/deploy/docker/nginx.conf)
  - 前端静态资源回退到 `index.html`
  - `/api/*` 转发给 `api:8000`
  - `/uploads/*` 转发给 `api:8000/uploads/*`
- [.env.server.example](/G:/codex/carbon-eye-campus/deploy/docker/.env.server.example)
  - 云端部署环境变量模板
- [build-on-server.sh](/G:/codex/carbon-eye-campus/deploy/docker/build-on-server.sh)
  - 云端一键构建并启动容器
- [install-docker-alinux3.sh](/G:/codex/carbon-eye-campus/deploy/docker/install-docker-alinux3.sh)
  - 阿里云 Linux 3 安装 Docker 的脚本

## 3. 环境变量怎么配

先在服务器上进入：

```bash
cd /opt/carbon-eye-campus/deploy/docker
cp .env.server.example .env
vi .env
```

需要重点改这些变量：

```env
MYSQL_ROOT_PASSWORD=你的MySQL root密码
MYSQL_APP_PASSWORD=应用连接数据库的密码
PUBLIC_UPLOAD_BASE_URL=http://你的公网IP/uploads
VISION_PROVIDER=ark
VISION_API_KEY=你的方舟API Key
VISION_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VISION_MODEL=doubao-seed-2-0-mini-260428
```

说明：

- `VISION_API_KEY` 只需要方舟提供的 API Key
- 当前代码不使用 AK/SK 签名方式
- 如果这里为空，图像识别不会正常调用模型

## 4. 第一次部署

### 4.1 安装 Docker

```bash
cd /opt/carbon-eye-campus
bash deploy/docker/install-docker-alinux3.sh
```

### 4.2 准备数据库初始化文件

脚本会优先找这两个文件之一：

- `/opt/carbon-eye-campus/deploy_artifacts/carbon_eye_dump.sql`
- `/opt/carbon-eye-campus/docs/database-schema.sql`

优先级说明：

- 有完整数据转储时，导入完整数据
- 没有完整数据时，至少导入建库建表 SQL

### 4.3 启动容器

```bash
cd /opt/carbon-eye-campus
bash deploy/docker/build-on-server.sh
```

这一步会做：

1. 检查 `docker` 是否已安装
2. 检查 `.env` 是否存在
3. 自动准备 MySQL 初始化 SQL
4. 构建 `api` 和 `web` 镜像
5. 启动 `db`、`api`、`web`

## 5. 日常更新流程

日常改代码后，不需要删整个服务器目录。

正确流程：

1. 本地修改代码
2. 只把改动后的代码同步到服务器 `/opt/carbon-eye-campus`
3. 在服务器执行：

```bash
cd /opt/carbon-eye-campus
docker compose -f deploy/docker/docker-compose.server-build.yml build
docker compose -f deploy/docker/docker-compose.server-build.yml up -d
```

如果你图省事，也可以继续直接跑：

```bash
cd /opt/carbon-eye-campus
bash deploy/docker/build-on-server.sh
```

## 6. 常用运维命令

查看容器状态：

```bash
cd /opt/carbon-eye-campus
docker compose -f deploy/docker/docker-compose.server-build.yml ps
```

查看后端日志：

```bash
docker logs -f carbon-eye-api
```

查看前端日志：

```bash
docker logs -f carbon-eye-web
```

查看数据库日志：

```bash
docker logs -f carbon-eye-db
```

重建后端：

```bash
cd /opt/carbon-eye-campus
docker compose -f deploy/docker/docker-compose.server-build.yml build api
docker compose -f deploy/docker/docker-compose.server-build.yml up -d api
```

重建前端：

```bash
cd /opt/carbon-eye-campus
docker compose -f deploy/docker/docker-compose.server-build.yml build web
docker compose -f deploy/docker/docker-compose.server-build.yml up -d web
```

停止整套服务：

```bash
cd /opt/carbon-eye-campus
docker compose -f deploy/docker/docker-compose.server-build.yml down
```

## 7. 前端为什么配置 `/api`

在 [web.Dockerfile](/G:/codex/carbon-eye-campus/deploy/docker/web.Dockerfile) 里：

```dockerfile
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}
```

意思是：

- 前端打包时，把接口根地址写成 `/api`
- 浏览器访问时，请求会变成：
  - `/api/dashboard`
  - `/api/uploads/images`
- 然后 Nginx 再把这些请求转发给后端容器

这样前端不需要写死公网 IP，也不需要直接暴露 FastAPI 端口。

## 8. Nginx 里的 `api:8000` 是什么

在 [nginx.conf](/G:/codex/carbon-eye-campus/deploy/docker/nginx.conf) 里：

```nginx
location /api/ {
    proxy_pass http://api:8000;
}
```

这里的 `api` 不是域名，是 Docker Compose 里的服务名。

也就是说：

- `web` 容器访问 `http://api:8000`
- 实际就是访问 `carbon-eye-api` 这个后端容器

这是 Docker 内网 DNS 自动提供的服务发现能力。

## 9. 为什么现在比原来方便

改成 Docker 后，主要好处不是“可以无脑乱传所有文件”，而是：

- 前后端和数据库的启动方式统一了
- 云端环境固定，不容易出现“本地能跑、服务器跑不起来”
- 依赖装在镜像层里，改源码时可以复用构建缓存
- 不再需要分别记 `npm build`、`systemctl restart`、数据库手工启动三套命令

你仍然应该避免：

- 删除整个 `/opt/carbon-eye-campus`
- 每次都把服务器清空重传

因为这样会把 Docker 构建缓存也一起浪费掉，部署反而变慢。

## 10. 当前推荐做法

以后默认按这套来：

1. 本地改代码
2. 同步到 `/opt/carbon-eye-campus`
3. 云端执行：

```bash
cd /opt/carbon-eye-campus
bash deploy/docker/build-on-server.sh
```

这是当前项目唯一保留、也是线上实际在用的部署链路。
