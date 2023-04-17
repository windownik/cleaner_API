import os

from fastapi import Depends
import starlette.status as _status
from lib import sql_connect as conn
from starlette.responses import Response, JSONResponse

from lib.response_examples import *
from lib.routes.push.push_func import send_push
from lib.sql_connect import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


@data_b.on_init
async def initialization(connect):
    # you can run your db initialization code here
    await connect.execute("SELECT 1")


@app.get(path='/send_push', tags=['Push'], responses=send_push_res)
async def send_push_notification(access_token: str, user_id: int, title: str, push_body: str, push_type: str,
                                 main_text: str = '0', db=Depends(data_b.connection)):
    """
    user_id - id of user for sending push\n
    title - Title of push\n
    push_body - Text body of push message\n
    main_text - Main text of message
    push_type - can be: read_bill,
    """
    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="not enough rights", status_code=_status.HTTP_401_UNAUTHORIZED)
    user_id = user_id[0][0]
    push_token = await conn.read_data(db=db, table='all_users', name='push', id_name='user_id', id_data=user_id)
    if not push_token:
        return Response(content="no user in database", status_code=_status.HTTP_400_BAD_REQUEST)
    send_push(fcm_token=push_token[0][0], title=title, body=push_body, main_text=main_text, push_type=push_type)
    return JSONResponse(content={'ok': True, 'desc': 'successful send push'},
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/update_push', tags=['Push'], responses=update_push_res)
async def find_phone_in_db(access_token: str, push_token: str, db=Depends(data_b.connection)):
    """Update users push token in database"""
    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="not enough rights", status_code=_status.HTTP_401_UNAUTHORIZED)
    user_id = user_id[0][0]
    await conn.update_data(db=db, table='all_users', name='push', data=push_token, id_name='id', id_data=user_id)

    return JSONResponse(content={'ok': True, 'desc': 'successfully updated'},
                        headers={'content-type': 'application/json; charset=utf-8'})