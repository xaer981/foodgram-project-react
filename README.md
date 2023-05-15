# Полное описание будет здесь после первого этапа
## Это описание на первый этап

Для запуска склонируйте репозиторий себе:
```
git clone https://github.com/xaer981/foodgram-project-react.git
```

```bash
cd foodgram-project-react/backend/api_foodgram/
```

Затем создайте виртуальное окружение и установите зависимости:

```bash
python -m venv venv
```

```bash
source venv/Scripts/activate
```

```bash
pip install -r requirements.txt
```

После этого необходимо выполнить миграции и можно запускать проект:

```
python manage.py migrate
```

##### Можно добавить в проект тестовые ингредиенты командой:
```
python manage.py import_data <Полный путь до файла ingredients.json>
```
например,
```
python manage.py import_data /d/Dev/foodgram-project-react/data/ingredients.json
```

Затем можно запускать:

```bash
python manage.py runserver
```


@xaer981
