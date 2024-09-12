# Ёлымтан
Ёлымтан - это переводчик с русского на мансийский и наоборот, доступный в качестве веб-страницы.

# Запуск локально
Создать файл `.env`, по параметрам указаным в example.env. Параметры:
- ```URL``` - это url бэкенд модели, куда можно обращаться. [Здесь](https://github.com/AInami-Rei/mansi_translator/blob/feature/model-mbart/model_backend/README.md) можно найти информацию по развертыванию модели.
```
cp example.env .env
```

Запустить `docker compose`:
```
docker compose up
```
Далее запустятся контейнеры с бэкендом и фронтендом. Фронт будет доступен по адресу `http://localhost:3000`, а бэкенд - по адресу `http://localhost:8000`.

# Деплой
Установить:
- nginx
- docker (и compose плагин)

Для начала нужно склонировать репозиторий:
```
git clone https://github.com/AInami-Rei/mansi_translator
cd mansi_translator
```

Затем:
```
cp .deploy/nginx.conf /etc/nginx/sites-enabled/site.conf
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

Заполнить файл `.env` следующими параметрами:
- `DOCKER_USERNAME` - логин пользователя, которому принадлежит образа бэкенда. В данном случае это `darrrinka`, так как текущий образ деплоится именно на репозиторий этого пользователя.
- `DOCKER_IMAGE` - имя образа бэкенда. В данном случае это `translator`.
- `DOCKER_IMAGE_TAG` - тег образа бэкенда. Может быть `latest` или другим тегом.
- `DOCKER_FRONTEND_IMAGE` - имя образа фронтенда. В данном случае это `translator-frontend`.
- `DOCKER_FRONTEND_IMAGE_TAG` - тег образа фронтенда. Может быть `latest` или другим тегом.
- `URL` - это url бэкенд модели, куда можно обращаться.

```
echo DOCKER_USERNAME=darrrinka >> .deploy/.env
echo DOCKER_IMAGE=translator >> .deploy/.env
echo DOCKER_IMAGE_TAG=latest >> .deploy/.env
echo DOCKER_FRONTEND_IMAGE=translator-frontend >> .deploy/.env
echo DOCKER_FRONTEND_IMAGE_TAG=latest >> .deploy/.env
echo URL=<url, где находится бэкенд модели> >> .deploy/.env
```
Затем можно запустить `docker compose`:
```
source .deploy/.env

docker compose -f .deploy/docker-compose.yml up -d
```

Для обновления версии нужно изменить версии тегов в `.env` и перезапустить `docker compose`.

[Репозиторий с образами бэкенда](https://hub.docker.com/repository/docker/darrrinka/translator)

[Репозиторий с образами фронтенда](https://hub.docker.com/repository/docker/darrrinka/translator-frontend)

Для быстрого обновления положить скрипт в папку пользователя
на сервере и запускать его с тегом:
```
cd ~
cp mansi_translator/scripts/update.sh .
chmod +x update.sh
./update.sh <тег>
```

# Лицензия
Этот репозиторий имеет лицензию GPL-2.0. Подробности можно найти в файле [LICENSE](https://github.com/AInami-Rei/mansi_translator/blob/dev/LICENSE).
