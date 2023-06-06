import datetime
import os

import starlette.status as _status
from fastapi import Depends
from starlette.responses import Response, JSONResponse

from lib import sql_connect as conn
from lib.db_objects import Order, User, Message
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
    access_token: access token in our service\n
    _______________\n
    status can be: created, search, return, finish, delete,
    """
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
    admin_id = await conn.get_token_admin(db=db, token_type='access', token=access_token)
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

    admin_comments = []
    admin_comments_data = await conn.get_orders_comment(db=db, order_id=order_id, user_to=order.creator_id,
                                                        admin=False if not admin_id else True)

    for msg_data in admin_comments_data:
        msg = Message(data=msg_data)
        admin_comments.append(
            msg.get_msg_json()
        )

    return JSONResponse(content={"ok": True,
                                 'order': order.dict(),
                                 "admin_comments": admin_comments,
                                 'from_user': user.get_user_json()},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/order', tags=['Orders'], responses=create_get_order_res)
async def update_order(access_token: str, order_id: int, city: str, street: str,
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

    order_data_1 = await conn.read_data(db=db, name='*', table='orders', id_name='order_id', id_data=order_id)
    if not order_data_1:
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

    await conn.create_msg(msg_id=order.order_id, msg_type='order_rework', title='Изменения ордера',
                          text=f'Пользователь сменил комментарий\n'
                               f'Старый: {order_data_1[0]["comment"]}\n\n'
                               f'Новый: {order_data[0]["comment"]}',
                          description='return',
                          lang='ru', from_id=user_id[0][0], to_id=0, user_type='admin', db=db)

    return JSONResponse(content={"ok": True,
                                 'description': 'order successfully updated',
                                 'order': order.dict()},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/order_status', tags=['Orders'], responses=create_get_order_res)
async def admin_confirm_ban_order(order_id: int, msg_id: int, status: str, access_token: str, comment: str = '0',
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

    if status not in ('ban', 'return', 'search_worker'):
        return Response(content="bad new status",
                        status_code=_status.HTTP_400_BAD_REQUEST)

    order_data = await conn.read_data(db=db, name='*', table='orders', id_name='order_id', id_data=order_id)
    if not order_data:
        return JSONResponse(content={"ok": False,
                                     'description': "Bad order_id"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    order = Order()
    order.from_db(order_data[0])

    await conn.update_data(db=db, table='message_line', name='status', id_data=msg_id, data="delete", id_name='id')
    await conn.update_data(db=db, table='message_line', name='deleted_date', id_data=msg_id,
                           data=datetime.datetime.now(), id_name='id')
    await conn.update_data(db=db, table='orders', name='status', id_data=order_id, data=status, id_name='order_id')
    await conn.update_data(db=db, table='orders', name='status_date', id_data=order_id, data=datetime.datetime.now(),
                           id_name='order_id')
    lang = await conn.read_data(table='all_users', id_name='user_id', id_data=user_id[0][0], name='lang', db=db)
    push_token = await conn.read_data(db=db, table='all_users', name='push', id_name='user_id',
                                      id_data=order.creator_id)
    if lang[0][0] == 'ru':
        title = 'Сообщение от модератора'
    elif lang[0][0] == 'he':
        title = 'Message from moderator'
    else:
        title = 'Message from moderator'

    if comment == 0:
        if lang[0][0] == 'ru':
            text = 'Сообщение от модератора\nСтатус вашего заказа обновлен'
        elif lang[0][0] == 'he':
            text = 'Message from moderator\nYour order status has been updated'
        else:
            text = 'Message from moderator\nYour order status has been updated'
    else:
        if lang[0][0] == 'ru':
            text = f'Сообщение от модератора\n{comment}'
        elif lang[0][0] == 'he':
            text = f'Message from moderator\n{comment}'
        else:
            text = f'Message from moderator\n{comment}'

    if push_token:
        await conn.create_msg(msg_id=order.order_id, msg_type='order_comment', title=title,
                              text=text,
                              description=status,
                              lang=lang[0][0], from_id=user_id[0][0], to_id=order.creator_id,
                              user_type='user', db=db)
        try:
            send_push(fcm_token=push_token[0][0], title=title, body=text, main_text=comment,
                      push_type='moder_order_msg')
        except Exception as _ex:
            print(_ex)

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

    orders_data = await conn.read_data_order(db=db, table='orders', id_name='creator_id', id_data=user_id[0][0])

    orders_list = []
    orders_in_deal = []

    for order in orders_data:
        _order = Order()
        _order.from_db(order)
        orders_list.append(_order.dict())
        if _order.status not in ('close', 'ban', 'finish', 'delete'):
            orders_in_deal.append(_order.order_id)

    return JSONResponse(content={"ok": True,
                                 "orders_in_deal": orders_in_deal,
                                 'orders': orders_list},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/all_orders_admin', tags=['Orders'], responses=get_all_order_res)
async def admin_get_all_orders(access_token: str, db=Depends(data_b.connection)):
    """Admin Get all from dataBase.\n
    access_token: access token in our service"""

    admin_id = await conn.get_token_admin(db=db, token_type='access', token=access_token)
    if not admin_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    orders_data = await conn.admin_read_orders(db=db, )
    orders_count = len(orders_data)

    orders_list = []

    for order in orders_data:
        _order = Order()
        _order.from_db(order)
        orders_list.append(_order.dict())

    return JSONResponse(content={"ok": True,
                                 "orders_count": orders_count,
                                 'orders': orders_list},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/admin_get_order', tags=['Orders'], responses=get_all_order_res)
async def admin_get_order_by_id(order_id: int, access_token: str, db=Depends(data_b.connection)):
    """Admin Get order from dataBase by order_id.\n
    access_token: access token in our service"""

    admin_id = await conn.get_token_admin(db=db, token_type='access', token=access_token)
    if not admin_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    orders_data = await conn.read_data(db=db, table='orders', id_name='order_id', id_data=order_id)

    orders_list = []

    for order in orders_data:
        _order = Order()
        _order.from_db(order)
        orders_list.append(_order.dict())

    return JSONResponse(content={"ok": True,
                                 'orders': orders_list},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.delete(path='/order', tags=['Orders'], responses=delete_order_res)
async def user_delete_orders(order_id: int, access_token: str, db=Depends(data_b.connection)):
    """User delete own order.\n
    order_id: id of order was delete\n
    access_token: access token in our service"""

    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    orders_data = await conn.read_data(db=db, table='orders', id_name='order_id', id_data=order_id)
    if not orders_data:
        return Response(content="bad order_id",
                        status_code=_status.HTTP_400_BAD_REQUEST)

    if orders_data[0]['creator_id'] != user_id[0][0]:
        return Response(content="no rights for delete",
                        status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.update_data(table='orders', name='status', data='delete', id_name='order_id', id_data=order_id, db=db)
    await conn.update_msg(name='status', data='delete', db=db, order_id=order_id, user_id=user_id[0][0])

    return JSONResponse(content={"ok": True,
                                 "description": 'The order was successfully deleted.'},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
