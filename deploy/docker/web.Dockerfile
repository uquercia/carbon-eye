FROM docker.m.daocloud.io/library/node:20-alpine AS build

# 前端构建阶段统一在 /app 内完成。
WORKDIR /app

COPY apps/web/package*.json ./

# 使用国内 npm 镜像，加快云端构建速度。
RUN npm config set registry https://registry.npmmirror.com \
    && npm install

COPY apps/web ./

# Vite 在构建时读取这个变量，告诉前端后端接口统一走 /api 反向代理。
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

FROM docker.m.daocloud.io/library/nginx:1.27-alpine

COPY deploy/docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
