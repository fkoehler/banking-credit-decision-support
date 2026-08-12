FROM node:22-alpine AS build
RUN corepack enable
WORKDIR /app
COPY services/web-ui/package.json services/web-ui/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY services/web-ui ./
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL
RUN pnpm build

FROM nginx:1.29-alpine
COPY services/web-ui/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
USER nginx
EXPOSE 8080
