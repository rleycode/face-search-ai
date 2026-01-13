import io
import face_recognition
import numpy as np
from fastapi import FastAPI, File, UploadFile, Header, HTTPException, Depends, BackgroundTasks
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType, utility
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from g_sheets import GoogleLogger

sheet_logger = GoogleLogger("google_creds.json", "face")

API_KEY = "secret-key-123"
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "faces_db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Подключаюсь к Milvus")
    connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
    
    if not utility.has_collection(COLLECTION_NAME):
        print("Создаю коллекцию")
        fields = [
            FieldSchema(name="pk", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, dim=128),
        ]
        schema = CollectionSchema(fields, "Хранилище векторов лиц")
        col = Collection(COLLECTION_NAME, schema)
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128},
        }
        col.create_index("embeddings", index_params)
        print("Коллекция готова")
    
    Collection(COLLECTION_NAME).load()
    print("Сервер готов к работе")
    
    yield 

    print("Отключаюсь от базы")
    connections.disconnect("default")

app = FastAPI(title="Face Search Microservice", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")


async def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key


@app.get("/ping")
async def ping():
    return {"status": "ok", "service": "Face Search v1"}

@app.post("/add_face/", dependencies=[Depends(verify_api_key)])
async def add_face_to_db(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    content = await file.read()
    image = face_recognition.load_image_file(io.BytesIO(content))
    

    encodings = face_recognition.face_encodings(image)
    if not encodings:
        return {"status": "error", "message": "Лицо на фото не найдено"}
    
    vector = encodings[0] 
    

    col = Collection(COLLECTION_NAME)
    mr = col.insert([[vector]]) 
    face_id = mr.primary_keys[0]
    background_tasks.add_task(sheet_logger.log_new_face, face_id)
    return {"status": "success", "db_id": mr.primary_keys[0], "message": "Лицо сохранено в базу"}

@app.post("/search/", dependencies=[Depends(verify_api_key)])
async def search_faces(file: UploadFile = File(...)):

    content = await file.read()
    image = face_recognition.load_image_file(io.BytesIO(content))
    

    encodings = face_recognition.face_encodings(image)
    if not encodings:
        return {"status": "error", "message": "Лицо на фото не найдено"}
    
    search_vector = encodings[0]
    
    col = Collection(COLLECTION_NAME)
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    
    results = col.search([search_vector], "embeddings", search_params, limit=3)
    
    found_faces = []
    for hits in results:
        for hit in hits:
            found_faces.append({"db_id": hit.id, "distance": hit.distance})
            
    return {"results": found_faces}