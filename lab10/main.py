from typing import Dict, List, Optional
from fastapi import FastAPI
from joblib import load
from tinydb import TinyDB, Query
from datetime import datetime
from tinydb.operations import set
import pandas as pd  

app = FastAPI(title="Lab 6")

# aquí carguen el modelo guardado (con load de joblib) y
model = load("modelo.joblib")
# el cliente de base de datos (con tinydb). Usen './db.json' como bbdd.
db =  TinyDB("./db.json")

# Nota: En el caso que al guardar en la bbdd les salga una excepción del estilo JSONSerializable
# conviertan el tipo de dato a uno más sencillo.
# Por ejemplo, si al guardar la predicción les levanta este error, usen int(prediccion[0])
# para convertirla a un entero nativo de python.

# Nota 2: Las funciones ya están implementadas con todos sus parámetros. No deberían
# agregar más que esos.


@app.post("/potabilidad/")
async def predict_and_save(observation: Dict[str, float]):
    observation_aux = pd.DataFrame.from_dict([observation])
    prediccion = model.predict(observation_aux)
    print(prediccion)
    # agregamos la fecha
    hoy = datetime.now()
    observation['potabilidad']= int(prediccion[0])
    observation['Day']=hoy.day
    observation['Month']= hoy.month
    observation['Year']= hoy.year
    id = db.insert(observation)
    return {'potabilidad':observation['potabilidad'],'id':id}


@app.get("/potabilidad/")
async def read_all():
    datos = db.all()
    return datos


@app.get("/potabilidad_diaria/")
async def read_by_day(day: int, month: int, year: int):
    potabilidad = Query()
    datos = db.search((potabilidad.Day==day) &
                    (potabilidad.Month==month) &
                    (potabilidad.Year==year))
    return datos


@app.put("/potabilidad/")
async def update_by_day(day: int, month: int, year: int, new_prediction: int):
    potabilidad = Query()
    ids = db.update(set('potabilidad',new_prediction),
                    ((potabilidad.Day==day) &
                    (potabilidad.Month==month) &
                    (potabilidad.Year==year)))
    return {'success': 0 if len(ids)== 0 else 1, "ids":ids}


@app.delete("/potabilidad/")
async def delete_by_day(day: int, month: int, year: int):
    potabilidad = Query()
    ids = db.remove((potabilidad.Day==day) &
                    (potabilidad.Month==month) &
                    (potabilidad.Year==year))
    return {'success': 0 if len(ids)== 0 else 1, "ids":ids}
