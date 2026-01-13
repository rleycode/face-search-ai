# Face Search Microservice

Микросервис для обратного поиска людей по фотографии.
Сервис принимает изображение, генерирует вектор лица и ищет наиболее похожие лица в векторной базе данных.

## Стек

*   Python 3.11
*   FastAPI (REST API)
*   face_recognition (детекция лиц и генерация эмбеддинго)
*   Milvus (векторная база данных, хранение и быстрый поиск)
*   Docker & Docker Compose (контейнеризация инфраструктуры)

## Запуск проекта

### 1. Предварительные требования
*   Установленный [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   Python 3.10 

### 2. Запуск инфраструктуры (Milvus)


```bash
docker-compose up -d
```


### 3. Установка зависимостей

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux or MacOS
python3 -m venv venv
source venv/bin/activate
```
Установка библиотек:
```bash
pip install -r requirements.txt
```

### 4. Запуск сервера
```bash
uvicorn main:app --reload
```

## Документация API
После запуска перейдите в Swagger UI для тестирования ручек:
http://127.0.0.1:8000/docs
Основные эндпоинты:
POST /add_face/ - Загрузить фото. Сервис найдет лицо, сгенерирует вектор и сохранит его в Milvus.
POST /search/ - Поиск. Загружаете фото, сервис ищет похожих людей в базе по L2-метрике.
distance < 0.6 - с высокой вероятностью это один и тот же человек.

Все методы защищены API-ключом.
При тестировании в Swagger введите:
secret-key-123
