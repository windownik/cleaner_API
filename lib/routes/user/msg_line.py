import os

import starlette.status as _status
from fastapi import Depends
from starlette.responses import Response, JSONResponse

from lib import sql_connect as conn
from lib.db_objects import User
from lib.response_examples import *
from lib.routes.push.push import send_push_notification
from lib.sql_connect import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


@data_b.on_init
async def initialization(connect):
    # you can run your db initialization code here
    await connect.execute("SELECT 1")


# Create new msg
@app.post(path='/create_msg', tags=['Message'], responses=new_msg_created_res)
async def create_new_messages(access_token: str, to_user_id: int, title: str, text: str, description: str,
                              user_type: str = 'user', lang: str = 'en',
                              msg_type: str = 'text', msg_id: int = 0, push: bool = False,
                              db=Depends(data_b.connection)):
    """
    Use this route for creating new message


    :param description:
    :param text:
    :param title:
    :param msg_id: id of new document or another main document. Send 0 if only text message
    :param access_token: user's access token in our service
    :param to_user_id: user_id for personal msg sending for all users send value 0
    :param user_type: can be 'user', 'admin', 'all'
    :param push: Send True for sending push notification
    :param lang: Can be 'en', 'ru', 'he'
    :param msg_type: Can be 'text', 'new_user', 'new_deal'
    :return: dict
    """
    from_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not from_id:
        return JSONResponse(content={"ok": False, "desc": "bad access token"},
                            status_code=_status.HTTP_401_UNAUTHORIZED)

    user_data = await conn.read_data(db=db, name='status', table='all_users', id_name='user_id',
                                     id_data=to_user_id)
    if not user_data and to_user_id != 0:
        return JSONResponse(content={"ok": False, "desc": "Bad to_user_id"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    if user_type not in ('user', 'admin', 'all'):
        return JSONResponse(content={"ok": False, "desc": "Bad user_type"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    if lang not in ('en', 'ru', 'he'):
        return JSONResponse(content={"ok": False, "desc": "Bad lang"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    msg_id = await conn.create_msg(msg_id=msg_id, msg_type=msg_type, title=title, text=text, description=description,
                                   lang=lang, from_id=from_id, to_id=to_user_id, user_type=user_type, db=db)
    if msg_id is None:
        return JSONResponse(content={"ok": False, "desc": "I can't create this message"},
                            status_code=_status.HTTP_400_BAD_REQUEST)
    if push:
        await send_push_notification(access_token=access_token, user_id=to_user_id, title=title, push_body=text,
                                     push_type='text_msg', db=db)

    return JSONResponse(content={"ok": True, 'desc': 'New message was created successfully.'},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/get_my_msg', tags=['Message'], responses=get_me_res)
async def get_all_my_messages(access_token: str, offset: int, limit: int, db=Depends(data_b.connection), ):
    """Here you can get new moder messages.
    access_token: This is access auth token. You can get it when create account or login"""
    user_id = await conn.get_token_admin(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    msg_data = await conn.read_all_msg(db=db, user_type='admin', lang='message_line', user_id=user_id[0][0])
    count = await conn.count_msg(db=db, table='message_line', name='')
    msg_list = []
    if not msg_data:
        return Response(content="no user in database",
                        status_code=_status.HTTP_401_UNAUTHORIZED)
    # # user = User(user_data[0])
    # return JSONResponse(content={"ok": True,
    #                              'count':
    #                              'user': user.get_user_json(),},
    #                     status_code=_status.HTTP_200_OK,
    #                     headers={'content-type': 'application/json; charset=utf-8'})
