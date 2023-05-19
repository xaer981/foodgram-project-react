# FoodGram
![Forkflow status](https://github.com/xaer981/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

http://foodgram-xaer981.sytes.net

## USERNAME AND PASSWORD FOR ADMIN:
- email: ```ritis@barauskas.ru```
- password: ```Ritis135531```

# Данный проект позволяет Вам:
- создавать рецепты
- просматривать и сохранять рецепты других пользователей в избранное
- добавлять рецепты в список покупок и скачивать удобно сформированный список необходимых ингредиентов из сохраннённых рецептов
- подписываться на любых авторов и быть в курсе их новых рецептов.

## Технологии:
- ![Python version](https://img.shields.io/pypi/pyversions/django)
- ![Django version](https://img.shields.io/pypi/v/django?label=django)
- ![DRF version](https://img.shields.io/pypi/v/djangorestframework?label=djangorestframework)
- ![Docker](https://img.shields.io/badge/using-Docker-green)
- ![Nginx](https://img.shields.io/badge/using-nginx-green)

### Процесс установки:
- Скопируйте репозиторий ```git clone https://github.com/xaer981/foodgram-project-react.git```
- Подключитесь к своему удалённому серверу ```ssh <username>@<ip>```
- Обновите существующие пакеты ```sudo apt update && sudo apt upgrade -y```
- Установите docker ```sudo apt install docker.io```
- Установите docker-compose ```curl -SL https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose```
- Дайте нужные разрешения docker-compose ```sudo chmod +x /usr/local/bin/docker-compose```
- Создайте нужные папки для проекта: ```mkdir -p projects/foodgram```
- Создайте там .env файл с вашими данными ```touch .env```
- Заполните его следующим образом:
```
ALLOWED_HOSTS=<ip 1> <ip 2>
CSRF_TRUSTED_ORIGINS=<ip 1> <ip 2>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<your db name>
POSTGRES_USER=<your postgres user>
POSTGRES_PASSWORD=<your postgres password>
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=<your django secret token>
```
- Скопируйте себе содержимое папки infra ```scp -r infra/* <usernamer>@<ip>:/home/<username>/projects/foodgram/```
- Запустите проект ```sudo docker-compose up -d```
- Выполните миграции ```sudo docker exec -it foodgram-backend python manage.py migrate```
- Соберите статику ```sudo docker exec -it foodgram-backend python manage.py collectstatic --no-input```
- Создайте суперпользователя ```sudo docker exec -it foodgram-backend python manage.py createsuperuser```

### Поздравляем, Вы великолепны!


@xaer981
