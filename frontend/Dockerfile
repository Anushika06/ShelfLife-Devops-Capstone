# ---- Stage 1: build the React app with Node ----
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY index.html vite.config.js ./
COPY public ./public
COPY src ./src
RUN npm run build

# ---- Stage 2: serve the static files with unprivileged Nginx ----
# nginx-unprivileged runs as UID 101 and listens on 8080 (no root, no port < 1024).
FROM nginxinc/nginx-unprivileged:1.31-alpine AS runtime
ARG APP_VERSION=dev
LABEL org.opencontainers.image.title="shelflife-frontend" \
      org.opencontainers.image.description="ShelfLife pantry tracker - React UI served by Nginx" \
      org.opencontainers.image.revision="${APP_VERSION}"
ENV BACKEND_URL=http://backend:8000
USER root
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
USER 101
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --start-period=30s --retries=3 \
  CMD wget -q -O /dev/null http://127.0.0.1:8080/healthz || exit 1
