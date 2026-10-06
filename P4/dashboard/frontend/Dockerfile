FROM node:26-alpine AS builder

WORKDIR /app

COPY ./package*.json ./

RUN npm ci

COPY index.html vite.config.js ./

COPY src ./src

RUN npm run build

FROM nginx:stable-alpine3.23-slim

COPY --chown=nginx:nginx --from=builder /app/dist /usr/share/nginx/html

COPY --chown=nginx:nginx ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
