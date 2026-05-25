FROM nginx:stable-alpine3.23-slim

RUN rm -rf /usr/share/nginx/html/*

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY index.html /usr/share/nginx/html/

RUN nginx -t

EXPOSE 80

ENTRYPOINT ["nginx", "-g", "daemon off;"]
