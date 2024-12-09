# Lab9

---

Проект реализует сервер для чата на основе WebSocket с использованием Tornado и Redis.
Он поддерживает обмен сообщениями в реальном времени, отображение списка онлайн пользователей и масштабируемую архитектуру благодаря Redis.

---

## Запуск

1. Клонируйте репозиторий:
    ```bash
    git clone https://github.com/keksik9/Lab9.git
    cd lab_9_otrpo
    ```


2. Запустите redis
    ```bash
    redis-server.exe  redis.windows.conf
    ```


3. Запустите приложение
    ```bash
      python main.py
    ```