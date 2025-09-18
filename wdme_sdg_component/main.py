import unexecore.debug
import waterverse_sdg.sdg as sdg

from pydantic import BaseModel
from typing import Any, List, Dict, Optional


from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware


origins = [
    "http://localhost",
    "http://localhost:63342",
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CurrentState(BaseModel):
    current_state:Dict[str, str]

class SensorDefiniton(CurrentState):
    properties:List[Dict[str, Any]]
    step: int
    reference_data: Optional[Dict[str, List[Dict[str,Any]]]] = None
    order: Optional[List[str]] = None


@app.post("/sdg/add_sensor_to_pilot")
def add_sensor_to_pilot(pilot:str, sensor:str, payload:SensorDefiniton, response: Response):

    try:
        sdg.add_pilot(pilot)
        data = payload.model_dump()

        if data['order'] == None:
            data.pop('order')

        if data['reference_data'] == None:
            data.pop('reference_data')

        if sdg.add_sensor_to_pilot(pilot, sensor,data):
            response.status_code = 201
        else:
            response.status_code = 422
    except Exception as e:
        response.status_code = 500
        return {unexecore.debug.exception_to_string(e)}

@app.get("/sdg/get_data")
async def get_data(pilot:str, sensor:str, steps:int, response: Response):
    try:
        return sdg.get_data(pilot, sensor, steps)

    except Exception as e:
        response.status_code = 422
        return {unexecore.debug.exception_to_string(e)}

@app.get("/sdg/get_info")
def get_info(response: Response):
    try:
        return sdg.pilot_model
    except Exception as e:
        response.status_code = 500
        return {unexecore.debug.exception_to_string(e)}

@app.put("/sdg/put_pilot_state")
def put_pilot_state(pilot:str, sensor:str, payload:CurrentState, response: Response):
    try:
        data = payload.model_dump()
        if sdg.set_current_state(pilot, sensor, data):
            response.status_code =200
        else:
            response.status_code=404
    except Exception as e:
        response.status_code = 500
        return {unexecore.debug.exception_to_string(e)}


@app.put("/sdg/reset_pilot_time")
def reset_pilot_time(pilot:str, fiware_time:str, response: Response):
    try:
        if sdg.reset_pilot(pilot, fiware_time):
            response.status_code =200
        else:
            response.status_code=404
    except Exception as e:
        response.status_code = 500
        return {unexecore.debug.exception_to_string(e)}

@app.delete("/sdg/delete_sensor_from_pilot")
def delete_sensor_from_pilot(pilot:str, sensor:str, response: Response):
    try:
        if sdg.delete_sensor_from_pilot(pilot, sensor):
            response.status_code = 200
        else:
            response.status_code = 404
    except Exception as e:
        response.status_code = 500
        return {unexecore.debug.exception_to_string(e)}

@app.get("/")
def default():
    return 'WATERVERSE SDG Component'

