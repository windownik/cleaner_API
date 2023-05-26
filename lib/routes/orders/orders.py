import datetime
import os

import starlette.status as _status
from fastapi import Depends
from starlette.responses import Response, JSONResponse

from lib import sql_connect as conn
from lib.db_objects import Order, User
from lib.response_examples import *
from lib.routes.push.push_func import send_push
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
    object_type_id: index of objects list from database\n
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

    new_order = await conn.write_order(db=db, creator_id=user_id[0][0], city=city, street=street, house=house_room,
                                       latitudes=latitudes, longitudes=longitudes, object_type_id=object_type_id,
                                       object_size=object_size, start_work=start_work, comment=comment,
                                       object_type_name_en=object_type[0]['name_en'],
                                       object_type_name_he=object_type[0]['name_heb'],
                                       object_type_name_ru=object_type[0]['name_ru'])
    order = Order()
    order.from_db(new_order[0])

    user = User(user_data[0])

    await conn.create_msg(msg_id=order.order_id, msg_type='new_order', title='Новый заказ на модерацию',
                          text=f'{user_data[0]["name"]}\n'
                               f'Адрес: {order.address.street} {order.address.house}, {order.address.city}',
                          description='0',
                          lang=user_data[0]['lang'], from_id=user_id[0][0], to_id=0, user_type='admin', db=db)

    return JSONResponse(content={'ok': True,
                                 'order': order.dict(),
                                 'from_user': user.get_user_json()
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

    order = Order()
    order.from_db(order_data[0])

    user_data = await conn.read_data(db=db, name='*', table='all_users', id_name='user_id', id_data=order.creator_id)

    user = User(user_data[0])

    return JSONResponse(content={"ok": True,
                                 'order': order.dict(),
                                 'from_user': user.get_user_json()},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/order', tags=['Orders'], responses=create_get_order_res)
async def get_order(access_token: str, order_id: int, city: str, street: str,
                    house_room: str, object_size: int, object_type_id: int, latitudes: float,
                    longitudes: float, start_work_time: str, comment: str,
                    db=Depends(data_b.connection)):
    """Get order from dataBase with id.\n
    order_id: id of order in dataBase\n
    city: city in object address\n
    street: street in object address\n
    house_room: number of house or room in address\n
    object_size: index of object size. Can be: 0, 1, 2 \n
    object_type_id: index of objects list from database\n
    comment: addition information for order\n
    start_work_time: date and time of start work. Example: 27-11-2023 14:35:45\n
    order_status: new status for order with id\n
    latitudes: (Широта) of home/work address\n
    longitudes: (Долгота) of home/work address\n
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

    order = Order()
    order.from_db(order_data[0])
    return JSONResponse(content={"ok": True,
                                 'description': 'order successfully updated',
                                 'order': order.dict()},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/order_status', tags=['Orders'], responses=create_get_order_res)
async def admin_confirm_ban_order(order_id: int, status: str, access_token: str, comment: str = '0',
                                  db=Depends(data_b.connection)):
    """Admin Send response while order will being checked.\n
    order_id: id of order in dataBase\n
    status: new order status, can be: ban, return, confirm\n
    comment: not necessary parameter. Put it when you want to send msg to order creator\n
    access_token: access token in our service"""
    user_id = await conn.get_token_admin(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token or now rights",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    if status not in ('ban', 'return', 'confirm'):
        return Response(content="bad new status",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    order_data = await conn.read_data(db=db, name='*', table='orders', id_name='order_id', id_data=order_id)
    if not order_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Bad order_id"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    order = Order()
    order.from_db(order_data[0])

    await conn.update_data(db=db, table='orders', name='status', id_data=order_id, data=status)
    await conn.update_data(db=db, table='orders', name='status_date', id_data=order_id, data=datetime.datetime.now())

    if comment != '0':
        push_token = await conn.read_data(db=db, table='all_users', name='push', id_name='user_id',
                                          id_data=order.creator_id)
        if push_token:
            await conn.create_msg(msg_id=order.order_id, msg_type='moder_order_msg', title='Message from moderator',
                                  text=comment,
                                  description='0',
                                  lang='en', from_id=user_id[0][0], to_id=order.creator_id,
                                  user_type='user', db=db)
            send_push(fcm_token=push_token[0][0], title='Message from moderator', body=comment, main_text=comment,
                      push_type='moder_order_msg')

    return JSONResponse(content={"ok": True,
                                 'description': "Order successfully updated."},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/all_orders', tags=['Orders'], responses=get_all_order_res)
async def user_get_orders(access_token: str, db=Depends(data_b.connection)):
    """Get all users orders from dataBase.\n
    access_token: access token in our service"""

    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    orders_data = await conn.read_data(db=db, table='orders', id_name='creator_id', id_data=user_id[0][0])

    orders_list = []
    orders_in_deal = []

    for order in orders_data:
        _order = Order()
        _order.from_db(order)
        orders_list.append(_order.dict())
        if _order.status not in ('close', 'ban', 'finish', 'deleted'):
            orders_in_deal.append(_order.order_id)

    return JSONResponse(content={"ok": True,
                                 "orders_in_deal": orders_in_deal,
                                 'orders': orders_list},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/all_orders_admin', tags=['Orders'], responses=get_all_order_res)
async def admin_get_orders(user_id: int, access_token: str, db=Depends(data_b.connection)):
    """Admin Get all users orders from dataBase.\n
    access_token: access token in our service"""

    admin_id = await conn.get_token_admin(db=db, token_type='access', token=access_token)
    if not admin_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    orders_data = await conn.read_data(db=db, table='orders', id_name='creator_id', id_data=user_id)
    orders_count = await conn.count_data(db=db, table='orders', id_name='creator_id', id_data=user_id)

    orders_list = []
    orders_in_deal = []

    for order in orders_data:
        _order = Order()
        _order.from_db(order)
        orders_list.append(_order.dict())
        if _order.status != 'close' or _order.status != 'ban' or _order.status != 'finish':
            orders_in_deal.append(_order.order_id)

    return JSONResponse(content={"ok": True,
                                 "orders_in_deal": orders_in_deal,
                                 "orders_count": orders_count[0][0],
                                 'orders': orders_list},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.delete(path='/order', tags=['Orders'], responses=delete_order_res)
async def admin_get_orders(order_id: int, access_token: str, db=Depends(data_b.connection)):
    """User delete own order.\n
    access_token: access token in our service"""

    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    orders_data = await conn.read_data(db=db, table='orders', id_name='order_id', id_data=order_id)
    if not orders_data:
        return Response(content="bad order_id",
                        status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.update_data(table='orders', name='status', data='delete', id_name='order_id', id_data=order_id, db=db)
    msg_id = await conn.update_msg(name='status', data='delete', db=db, order_id=order_id, user_id=user_id[0][0])
    if not msg_id:
        return Response(content="Error with update message",
                        status_code=_status.HTTP_400_BAD_REQUEST)

    return JSONResponse(content={"ok": True,
                                 "msg": msg_id[0][0],
                                 "count": len(msg_id),
                                 "description": 'The order was successfully deleted.'},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
