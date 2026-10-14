FROM nginx:1.27-alpine
# 預設名字：docker run -e DEFAULT_NAME_LATIN=... -e DEFAULT_NAME_CN=...（留空用 index.html 內建值）
ENV DEFAULT_NAME_LATIN= DEFAULT_NAME_CN= NGINX_ENVSUBST_OUTPUT_DIR=/usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY site/ /usr/share/nginx/html/
COPY config.js.template /etc/nginx/templates/
EXPOSE 80
