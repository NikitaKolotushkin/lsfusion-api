# lsfusion-api
API-gateway for LSFusion 

## Установка
```sh

git clone https://github.com/NikitaKolotushkin/lsfusion-api.git
cd lsfusion-api

docker compose build
docker compose up -d

```

Далее необходимо перейти в адресной строке браузера:
http://127.0.0.1:8000/docs#/ (Swagger UI)
http://127.0.0.1:8080/ (Графический интерфейс LSFusion)