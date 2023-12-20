# FoodGram
![Forkflow status](https://github.com/xaer981/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Данный проект позволяет Вам:
- 🍖 создавать рецепты
- ⭐ просматривать и сохранять рецепты других пользователей в избранное
- 🛒 добавлять рецепты в список покупок и скачивать удобно сформированный список необходимых ингредиентов из сохраннённых рецептов
- ❤️ подписываться на любых авторов и быть в курсе их новых рецептов.

## Технологии:
- ![Python version](https://img.shields.io/pypi/pyversions/django)
- ![Django version](https://img.shields.io/pypi/v/django?label=django)
- ![DRF version](https://img.shields.io/pypi/v/djangorestframework?label=djangorestframework)
- ![Docker](https://img.shields.io/badge/using-Docker-green)
- ![Nginx](https://img.shields.io/badge/using-nginx-green)

### Процесс установки:
- Скопируйте репозиторий ```git clone https://github.com/xaer981/foodgram-project-react.git```
- <details>
    <summary>Для запуска на удалённом сервере</summary>
      <li>Подключитесь к своему удалённому серверу <code>ssh {username}@{ip}</code></li>
      <li>Обновите существующие пакеты <code>sudo apt update && sudo apt upgrade -y</code></li>
      <li>Установите docker <code>sudo apt install docker.io</code></li>
      <li>Установите docker-compose <code>curl -SL https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose</code></li>
      <li>Дайте нужные разрешения docker-compose <code>sudo chmod +x /usr/local/bin/docker-compose</code></li>
      <li>Создайте нужные папки для проекта: <code>mkdir -p projects/foodgram</code></li>
      <li>Скопируйте себе содержимое папки infra <code>scp -r infra/* {username}@{ip}:/home/{username}/projects/foodgram/</code></li>
  </details>
- Создайте .env файл с вашими данными ```touch .env``` в папке infra/
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
> [!NOTE]
> Если у Вас Windows, выполняйте команды ниже без `sudo`.
- Запустите проект ```sudo docker-compose up -d```
- Выполните миграции ```sudo docker exec -it foodgram-backend python manage.py migrate```
- Соберите статику ```sudo docker exec -it foodgram-backend python manage.py collectstatic --no-input```
- Создайте суперпользователя ```sudo docker exec -it foodgram-backend python manage.py createsuperuser```

### Поздравляем, Вы великолепны! 🏆

<p align=center>
  <a href="url"><img src="https://github.com/xaer981/xaer981/blob/main/main_cat.gif" align="center" height="40" width="128"></a>
</p>
