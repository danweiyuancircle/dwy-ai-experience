# 构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

COPY . .

RUN corepack enable && pnpm install --frozen-lockfile && pnpm build

# 生产阶段
FROM nginx:alpine

COPY --from=builder /app/apps/web/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
