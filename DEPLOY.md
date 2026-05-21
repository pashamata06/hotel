# Деплой на Render.com

1. Создай аккаунт на render.com

2. Создай новый Web Service:
   - Connect GitHub репозиторий
   - Environment: Docker
   - Настройки:
     - Build Command: docker build -t hotel-app .
     - Start Command: docker run -p 8000:8000 hotel-app

3. Создай PostgreSQL базу данных на Render

4. Добавь переменные окружения в Web Service:
   - DEBUG=0
   - DB_NAME=...
   - DB_USER=...
   - DB_PASSWORD=...
   - DB_HOST=...
   - DB_PORT=5432

5. Деплой
