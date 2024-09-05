# Ёлымтан
Ёлымтан - это переводчик с русского на мансийский и наоборот, доступный в качестве веб-страницы.

# Запуск
Перед запуском необходимо создать в корневой директории файл ```.env``` и заполнить его переменными окружения, указанными в файле ```example.env```. В нем есть такие параметры как:
- ```TEMPERATURE``` - температура для генерации модели. Чем выше, тем модель генерирует более разнообразно.
- ```MODELS``` - названия моделей, доступные для генерации.

После создания ```.env``` файла, необходимо запустить ```docker-compose```:
```bash
docker compose up -d
```

Образ сбилдится и запустится автоматически.

# Использование готового образа
При каждом релизе новый образ пушится [сюда](https://hub.docker.com/repository/docker/darrrinka/translator/general). Его можно спуллить и запустить, перед этим создав файл ```.env``` в корневой директории и заполнив его переменными окружения, указанными в файле ```example.env```.
```
docker pull darrrinka/translator:7
docker run -d -p 8000:8000 --env-file .env darrrinka/translator:7
```

# Лицензия
Этот репозиторий имеет лицензию GPL-2.0. Подробности можно найти в файле [LICENSE](https://github.com/AInami-Rei/mansi_translator/blob/dev/LICENSE).
