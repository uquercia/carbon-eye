FROM docker.m.daocloud.io/library/node:20-alpine AS build

# 前端构建阶段。
WORKDIR /app

COPY apps/web/package*.json ./

# 使用国内 npm 镜像，加快云端依赖安装。
RUN npm config set registry https://registry.npmmirror.com \
    && npm install

COPY apps/web ./

# Vite 在构建时读取该变量，让浏览器接口请求统一走 nginx 的 /api。
ARG VITE_API_BASE_URL=/api
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

FROM docker.m.daocloud.io/library/nginx:1.27-alpine

COPY deploy/docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
# 将答辩 HTML 页面一起打进 nginx 镜像，供 /api/html/ 与 /defense/ 访问。
COPY docs/ppt-html /usr/share/nginx/html/api/html

EXPOSE 80
