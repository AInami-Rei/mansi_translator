#!/bin/bash

# Проверяем, передан ли параметр
if [ $# -eq 0 ]; then
    echo "Ошибка: Не передан параметр для тега."
    echo "Использование: $0 <tag>"
    exit 1
fi

# Получаем значение тега из параметра
TAG=$1

# Путь к файлу .env
ENV_FILE="mansi_translator/.deploy/.env"

# Обновляем значения в файле .env
sed -i "s/DOCKER_IMAGE_TAG=.*/DOCKER_IMAGE_TAG=$TAG/" $ENV_FILE
sed -i "s/DOCKER_FRONTEND_IMAGE_TAG=.*/DOCKER_FRONTEND_IMAGE_TAG=$TAG/" $ENV_FILE

# Выводим обновленное содержимое файла
echo "Обновленный файл .env:"
cat $ENV_FILE

# Загружаем переменные из .env файла
source $ENV_FILE

# Запускаем docker-compose
docker compose -f mansi_translator/.deploy/docker-compose.yml up -d

echo "Docker Compose запущен с тегом: $TAG"
