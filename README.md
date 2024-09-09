# Ёлымтан
Ёлымтан - это переводчик с русского на мансийский и наоборот, доступный в качестве веб-страницы.

# Запуск
Перед запуском необходимо создать в корневой директории файл ```.env``` и заполнить его переменными окружения, указанными в файле ```example.env```. В нем есть такие параметры как:
- ```URL``` - url, где находится бэкенд модели.

После создания ```.env``` файла, необходимо запустить ```docker-compose```:
```bash
docker compose up -d
```

Образ сбилдится и запустится автоматически.

# Использование готового образа
При каждом релизе новый образ пушится [сюда](https://hub.docker.com/repository/docker/darrrinka/translator/general). Его можно спуллить и запустить, перед этим создав файл ```.env``` в корневой директории и заполнив его переменными окружения, указанными в файле ```example.env```.
```
docker pull darrrinka/translator:latest
docker run -d -p 8000:8000 --env-file .env darrrinka/translator:latest
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

echo DOCKER_USERNAME=<your docker username> > .env

echo DOCKER_IMAGE=<your docker repository> > .env
echo DOCKER_IMAGE_TAG=<your docker image tag> > .env

echo DOCKER_FRONTEND_IMAGE=<your docker frontend repository> > .env
echo DOCKER_FRONTEND_IMAGE_TAG=<your docker frontend image tag> > .env

source .env

docker compose -f .deploy/docker-compose.yml up -d
```

Для обновления версии нужно изменить версии тегов в `.env` и перезапустить `docker compose`.

# Лицензия
Этот репозиторий имеет лицензию GPL-2.0. Подробности можно найти в файле [LICENSE](https://github.com/AInami-Rei/mansi_translator/blob/dev/LICENSE).
