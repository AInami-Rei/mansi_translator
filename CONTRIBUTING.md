# Branch and commit naming
При создании веток и коммитов следуй https://dev.to/varbsan/a-simplified-convention-for-naming-branches-and-commits-in-git-il4.

# Pull requests
В данном проекте основная ветка для разработки - dev. Когда ты создал свою ветку, создай pull request в ветку dev. Основные и работающие релизы будут далее мержиться в ветку main.

# Установка зависимостей
Мы используем poetry, поэтому тебе нужно скачать его (как - см. здесь https://python-poetry.org/) и установить зависимости проекта:
```
poetry install
```

# Pre-commit
Мы используем хуки - pre-commit. Перед созданием ветки или коммита, установи pre-commit в своем окружении и выполни следующую команду:
```
pre-commit install
```
После этого перед каждым коммитом будут выполняться хуки. Если хуки успешно пройдены, то коммит создастся, иначе вы получите сообщение о том, что необходимо исправить ошибки. Линтеры автоматически исправляют ошибки, поэтому после этого нужно снова добавить в индекс файл, который был исправлен, и сделать коммит.

# CI-CD | GitHub Actions
На всех ветках происходит тестовый билд бэкенд и фронтенд докер-образов. Очень важно его отслеживать. Если он не удастся, pull request мержить нельзя.

На ветках dev и main после тестового билда докер-образов они пушатся в соответствующие репозитории, где тег - это номер github action.
