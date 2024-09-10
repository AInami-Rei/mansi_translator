# Ёлымтан
Ёлымтан - это переводчик с русского на мансийский и наоборот, доступный в качестве веб-страницы.

# Разработка
Создать файл `.env`:
```
cp .env.example .env
echo URL=<url, где находится бэкенд модели> >> .env
```

Запустить `docker compose`:
```
docker compose up
```

# Деплой
Для начала нужно склонировать репозиторий:
```
git clone https://github.com/AInami-Rei/mansi_translator
cd mansi_translator
```

Установить nginx, затем:
```
cp .deploy/nginx.conf /etc/nginx/sites-enabled/site.conf
sudo nginx -t
sudo systemctl restart nginx
```

Заполнить файл `.env`, а затем запустить `docker compose`:
```
cp .env.example .env

echo DOCKER_USERNAME=darrrinka > .env
echo DOCKER_IMAGE=translator > .env
echo DOCKER_IMAGE_TAG=latest > .env
echo DOCKER_FRONTEND_IMAGE=translator-frontend > .env
echo DOCKER_FRONTEND_IMAGE_TAG=latest > .env
echo URL=<url, где находится бэкенд модели> >> .env

source .env

docker compose -f .deploy/docker-compose.yml up -d
```

Для обновления версии нужно изменить версии тегов в `.env` и перезапустить `docker compose`.

[Репозиторий с образами бэкенда](https://hub.docker.com/repository/docker/darrrinka/translator)

[Репозиторий с образами фронтенда](https://hub.docker.com/repository/docker/darrrinka/translator-frontend)

# Лицензия
Этот репозиторий имеет лицензию GPL-2.0. Подробности можно найти в файле [LICENSE](https://github.com/AInami-Rei/mansi_translator/blob/dev/LICENSE).
