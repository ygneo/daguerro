server {
  listen 80;
  server_name www.mydomain.com;
  rewrite ^/(.*) http://mydomain.com/$1 permanent;
}

server {
  listen 80;
  server_name mydomain.com;

  access_log /sites/mydomain.com/logs/access.log;
  error_log /sites/mydomain.com/logs/error.log;

  location /media {
    root /sites/mydomain.com/media;
  }

  location / {
    proxy_pass http://127.0.0.1:29000;
  }
}