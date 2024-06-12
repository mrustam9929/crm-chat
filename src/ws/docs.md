## Документация по WS для фронтенда

### URL: ```ws://{domain}/connect/?token={keycloak_token}```

### Общий вид события:

```json
{
  "event_type": "event_type",
  "data": {
    "field1": "value1",
    "field2": "value2",
    ...
  }
}
```

### Типы события:

>1. Статус пользователя (подключился/отключился)
   событие получит все кураторы

- user_id -> id пользователя
- status -> online/offline

```json
{
  "event_type": "user_status",
  "data": {
    "user_id": "<user_id>",
    "status": "online/offline"
  }
}
```

>2. Новый чат (пользователь начал новый чат)
   событие получит все кураторы у кого есть доступ к теме чата и клиент чата

- user_id -> id пользователя (клиент)
- chat_id -> чат
- chat_type -> order/topic (тип чата)

```json
{
  "event_type": "new_chat",
  "data": {
    "user_id": "<user_id>",
    "chat_id": "<chat_id>",
    "chat_type": "order/topic"
  }
}
```

>3. Новое сообщение в чате

```json
{
  "event_type": "new_message",
  "data": {
    "id": "message_id",
    "sender": "user_id",
    "chat_id": "chat_id",
    "text": "text",
    "message_type": "text/file/emoji",
    "created_at": "2021-01-01T00:00:00",
    "files": {
      "id": "int",
      "file": "<file_url>"
    }
  }
}
```

> 4. Назначение куратора на чат

```json
{
  "event_type": "assign_curator",
  "data": {
    "chat_id": "chat_id",
    "curator_id": "curator_id"
  }
}
```

> 5. Изменение статуса чата

```json
{
  "event_type": "update_chat_status",
  "data": {
    "chat_id": "chat_id",
    "status": "<status>"
  }
}
```

> 6. Прочитанное сообщение

```json
{
  "event_type": "read_chat_message",
  "data": {
    "chat_id": "chat_id",
    "last_message_id": "<last_message_id>",
    "user_id": "<user_id>"
  }
}
```

> 7. Сообщение было удалено

```json
{
  "event_type": "delete_message",
  "data": {
    "chat_id": "chat_id",
    "message_id": "<message_id>"
  }
}
```

> 8. Cообщение было отредактировано

```json
{
  "event_type": "update_message",
  "data": {
    "id": "message_id",
    "sender": "user_id",
    "chat_id": "chat_id",
    "text": "text",
    "message_type": "text/file/emoji",
    "created_at": "2021-01-01T00:00:00",
    "files": {
      "id": "int",
      "file": "<file_url>"
    }
  }
}
```