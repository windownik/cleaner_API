import os

import starlette.status as _status
from fastapi import Depends
from starlette.responses import Response, JSONResponse

from lib import sql_connect as conn
from lib.db_objects import User
from lib.response_examples import *
from lib.sql_connect import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


@app.post(path='/order', tags=['Orders'], responses=create_user_res)
async def create_new_order(city: str, street: str, house_room: str, object_size: int, object_index: int,
                           latitudes: float, longitudes: float, start_work_time: str, comment: int, access_token: str,
                           db=Depends(data_b.connection)):
    """Create new order in server.
    city: city in object address\n
    street: street in object address\n
    house_room: number of house or room in address\n
    object_size: index of object size. Can be: 0, 1, 2 \n
    object_index: index of objects list from database\n
    comment: addition information for order\n
    start_work_time: date and time of start work time\n
    latitudes: (Широта) of home/work address\n
    longitudes: (Долгота) of home/work address\n
    access_token: Facebook access token"""
    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)
    user_data = await conn.read_data(db=db, name='*', table='all_users',
                                     id_name='user_id', id_data=user_id[0][0])
    if not user_data:
        return Response(content="no user in database",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    # await conn.
    user = User(user_data[0])
    return JSONResponse(content={"ok": True,
                                 'user': user.get_user_json(),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
