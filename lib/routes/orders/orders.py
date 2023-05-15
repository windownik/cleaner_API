import datetime
import os

import starlette.status as _status
from fastapi import Depends
from starlette.responses import Response, JSONResponse

from lib import sql_connect as conn
from lib.db_objects import Order
from lib.response_examples import *
from lib.sql_connect import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


@app.post(path='/order', tags=['Orders'], responses=create_get_order_res)
async def create_new_order(city: str, street: str, house_room: str, object_size: int, object_type_id: int,
                           latitudes: float, longitudes: float, start_work_time: str, comment: str, access_token: str,
                           db=Depends(data_b.connection)):
    """Create new order in server.
    city: city in object address\n
    street: street in object address\n
    house_room: number of house or room in address\n
    object_size: index of object size. Can be: 0, 1, 2 \n
    object_index: index of objects list from database\n
    comment: addition information for order\n
    start_work_time: date and time of start work. Example: 27-11-2023 14:35:45\n
    latitudes: (Широта) of home/work address\n
    longitudes: (Долгота) of home/work address\n
    access_token: access token in our service"""
    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)
    user_data = await conn.read_data(db=db, name='*', table='all_users',
                                     id_name='user_id', id_data=user_id[0][0])
    if not user_data:
        return JSONResponse(content={"ok": False,
                                     'description': "no user in database"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    object_type = await conn.read_data(table='object_type', id_name='id', id_data=object_type_id, db=db)
    if not object_type:
        return JSONResponse(content={"ok": False,
                                     'description': "I haven't this object_type_id in database"},
                            status_code=_status.HTTP_400_BAD_REQUEST)
    try:
        start_work = datetime.datetime.strptime(start_work_time, '%d-%m-%Y %H:%M:%S')
    except Exception as _ex:
        print("Create order error!", _ex)
        return JSONResponse(content={"ok": False,
                                     'description': "Bad data in str start_work_time"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    new_order = await conn.write_order(db=db, creator_id=user_id, city=city, street=street, house=house_room,
                                       latitudes=latitudes, longitudes=longitudes, object_type_id=object_type_id,
                                       object_size=object_size, start_work=start_work, comment=comment,
                                       object_type_name_en=object_type[0]['name_en'],
                                       object_type_name_he=object_type[0]['name_heb'],
                                       object_type_name_ru=object_type[0]['name_ru'])

    order = Order.parse_obj(new_order[0])
    return JSONResponse(content={"ok": True,
                                 'order': order.dict(),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/order', tags=['Orders'], responses=create_get_order_res)
async def get_order(order_id: int, access_token: str, db=Depends(data_b.connection)):
    """Get order from dataBase with id.\n
    order_id: id of order in dataBase\n
    access_token: access token in our service"""
    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)
    order_data = await conn.read_data(db=db, name='*', table='orders', id_name='order_id', id_data=order_id)
    if not order_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Bad order_id"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    order = Order.parse_obj(order_data[0])
    return JSONResponse(content={"ok": True,
                                 'order': order.dict()},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/order', tags=['Orders'], responses=create_get_order_res)
async def get_order(access_token: str, order_id: int, city: str = '0', street: str = '0',
                    house_room: str = '0', object_size: int = 0, object_type_id: int = 0, latitudes: float = 0,
                    longitudes: float = 0, start_work_time: str = '0', comment: str = '0',
                    db=Depends(data_b.connection)):
    """Get order from dataBase with id.\n
    order_id: id of order in dataBase\n
    order_status: new status for order with id\n
    access_token: access token in our service"""

    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    order_data = await conn.read_data(db=db, name='*', table='orders', id_name='order_id', id_data=order_id)
    if not order_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Bad order_id"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    object_type = await conn.read_data(table='object_type', id_name='id', id_data=object_type_id, db=db)
    if not object_type:
        return JSONResponse(content={"ok": False,
                                     'description': "I haven't this object_type_id in database"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    try:
        start_work = datetime.datetime.strptime(start_work_time, '%d-%m-%Y %H:%M:%S')
    except Exception as _ex:
        print("Create order error!", _ex)
        return JSONResponse(content={"ok": False,
                                     'description': "Bad data in str start_work_time"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    order_data = await conn.update_order(db=db, city=city, street=street, house=house_room, longitudes=longitudes,
                                         latitudes=latitudes, object_size=object_size, object_type_id=object_type_id,
                                         object_type_name_en=object_type[0]['name_en'],
                                         object_type_name_he=object_type[0]['name_heb'],
                                         object_type_name_ru=object_type[0]['name_ru'], comment=comment,
                                         start_work=start_work, order_id=order_id)

    if not order_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Get some error with update"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    order = Order.parse_obj(order_data[0])
    return JSONResponse(content={"ok": True,
                                 'description': 'order successfully updated',
                                 'order': order.dict()},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
