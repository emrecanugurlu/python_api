from enum import Enum
from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import datetime
import psycopg2
import random
import datetime
import uuid
from .database import SessionLocal, engine
from . import models
from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

try:
    connection = psycopg2.connect(host='localhost', database='postgres', user='postgres', password='123456')
    print("Veritabanı bağlantısı başarılı")
except psycopg2.Error as e:
    print(f"Hata: Veritabanı bağlantısı başarısız oldu: {e}")


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/sqlalchemy")
async def deneme(db: Session = Depends(get_db)):
    products = db.query(models.Product).all()
    return {"status" : products}


@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}


@app.get("/products")
async def get_products():
    try:
        cursor = connection.cursor()
        query = " Select * From product"
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Veriler getirilirken hata oluştu {e}")


@app.get("/product/{id}")
async def get_product_by_id(id):
    cursor = connection.cursor()
    print(id)
    cursor.execute(f""" SELECT * FROM product WHERE id = '{id}' """)
    result = cursor.fetchone()
    return result


@app.post("/product", status_code=status.HTTP_201_CREATED)
async def add_product(name: str, description: str, price: float, quantity: int):
    try:
        cursor = connection.cursor()
        id: uuid = uuid.uuid4()
        created_at: datetime = datetime.datetime.now()
        updated_at: datetime = datetime.datetime.now()
        cursor.execute(
            "INSERT INTO product (id, name, description, price, quantity, created_at, updated_at) VALUES (%s,%s,%s,%s,%s,%s,%s) returning *", (str(id), name, description, str(price), str(quantity), str(created_at), str(updated_at)))
        result = cursor.fetchone()
        connection.commit()
        return result
    except psycopg2.Error as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")


@app.delete("/product/{id}")
async def delete_product(id):
    try:
        cursor = connection.cursor()
        cursor.execute(f""" DELETE FROM product WHERE id = '{id}' """)
        connection.commit()
        return "Veri silme işlemi başarıyla gerçekleştirilmiştir..."
    except psycopg2.Error as error:
        return "Hata"
    

@app.put("/products/{id}")
async def update_product(id, name, description, price, quantity):
    try:
        cursor = connection.cursor()
        updated_at: datetime = datetime.datetime.now()
        cursor.execute(f""" UPDATE product SET name = '{name}', description= '{description}', price= {price}, quantity= {quantity}, updated_at = '{updated_at}'  WHERE id = '{id}' RETURNING * """)
        result = cursor.fetchone()
        connection.commit()
        return result
    except:
        return "Hata"
