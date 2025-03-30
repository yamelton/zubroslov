# HTTP -> HTTPS редирект
server {
    listen 80;
    server_name zubroslov.ru;
    return 301 https://$host$request_uri;
}

# HTTPS сервер
server {
    listen 443 ssl;
    server_name zubroslov.ru;

    # SSL настройки
    ssl_certificate /etc/letsencrypt/live/zubroslov.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/zubroslov.ru/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Безопасность
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Специальная обработка для корневого URL
    location = / {
        proxy_pass https://storage.yandexcloud.net/zubroslov.ru/index.html;
        proxy_set_header Host storage.yandexcloud.net;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Оптимизация для статических файлов
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        proxy_pass https://storage.yandexcloud.net/zubroslov.ru$request_uri;
        proxy_set_header Host storage.yandexcloud.net;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        expires 30d;
        add_header Cache-Control "public, max-age=2592000";
        access_log off;
    }

    # Основной прокси для всех остальных запросов
    location / {
        proxy_pass https://storage.yandexcloud.net/zubroslov.ru/;
        proxy_set_header Host storage.yandexcloud.net;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
