# Foodgram

![](https://github.com/alex-b1234/foodgram-project-react/actions/workflows/main.yml/badge.svg)

### Foodgram - это сервис для публикации рецептов

## Запуск
```
cd infra/
```
```
docker compose up
```

## Сервер
url: taskisanek.ddns.net\
admin_user: admin\
password: adminadmin

## Запросы к api
Регистрация:\
<b>POST</b> /api/users/
```
{
    "email": "vpupkin@yandex.ru",
    "username": "vasya.pupkin",
    "first_name": "Вася",
    "last_name": "Пупкин",
    "password": "Qwerty123"
}
```

Список рецептов:\
<b>GET</b> /api/recipes/

Создание рецептов:\
<b>POST</b> /api/recipes/
```
{

    "ingredients": 

[

    {
        "id": 1123,
        "amount": 10
    }

],
"tags": 

    [
        1,
        2
    ],
    "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
    "name": "string",
    "text": "string",
    "cooking_time": 1

}
```