server {
    server_name api.zubroslov.ru;

    # Директива для статических файлов (аудио)
    location /static/ {
        alias /var/www/static/;  # Путь к аудиофайлам на сервере
        expires 30d;         # Кэширование в браузере на 30 дней
        access_log off;      # Отключить логирование статики
    }

    # Проксирование API-запросов на бэкенд
    location / {
        proxy_pass http://localhost:8000;  # Порт бэкенда
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/api.zubroslov.ru/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/api.zubroslov.ru/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

}
server {
    if ($host = api.zubroslov.ru) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    listen 80;
    server_name api.zubroslov.ru;
    return 404; # managed by Certbot


}
