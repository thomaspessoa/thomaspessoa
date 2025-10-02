FROM nginx:alpine

# Copy the static files. Paths are relative to build context './frontend'
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY script.js /usr/share/nginx/html/

# Copy the Nginx configuration. Path is relative to build context './frontend'
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]