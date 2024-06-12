## СТЕК

- Django
- DRF
- Django Channels
- PostgreSQL
- Redis

## **Запуск проекта**

> docker-compose up -d --build

### **Контейнеры**

* django app - port 8000
* daphne - port 8001
* dozzle - port 8080


#### Создать суперадмина для админки Django

> docker-compose exec app ./manage.py createsuperuser

## Документация API SWAGGER

> http://localhost/api/v1/docs/

## **ENV**

```env
DEVELOPMENT_MODE=PRODUCTION or DEVELOPMENT

# DJANGO CORE SETTINGS
SECRET_KEY=
ALLOWED_HOSTS=* # домен через пробел

# DATABASE SETTINGS
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST='postgres'
DB_PORT='5432'

# REDIS
REDIS_HOST=redis
REDIS_PORT=6379

# CONSTANTS
CHAT_MESSAGE_FILE_MAX_SIZE=20 # Максимальный размер файла в мегабайтах
CHAT_MESSAGE_ALLOWED_FILE_EXTENSIONS=xls,xlsx,doc,docx,pdf,jpg,png,pptx,mp4,avi,3gpp


LOG_FILES_PATH= # Путь к папке с логами

# KEYCLOAK SETTINGS
KEYCLOAK_SERVER_URL=
KEYCLOAK_CLIENT_ID=
KEYCLOAK_REALM_NAME=
KEYCLOAK_CLIENT_SECRET_KEY=


KEYCLOAK_CLIENT_ROLE= # Роль клиента в keycloak по умолчанию chat_user
KEYCLOAK_CURATOR_ROLE= # Роль куратора в keycloak по умолчанию chat_manager
```

## **Dozzle**

#### Мониторинг логов контейнеров

Нужно добавить доступы в файл [users.yml](etc%2Fcompose%2Fdozzle%2Fdata%2Fusers.yml)
> http://localhost:8080/

## Документация по WS

[docs.md](src/ws/docs.md)



