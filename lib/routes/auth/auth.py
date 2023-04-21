import os

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib import sql_connect as conn
from lib.check_access_fb import user_fb_check_auth
from lib.db_objects import User
from lib.response_examples import *
from lib.sql_connect import data_b, app

ip_server = os.environ.get("IP_SERVER")
ip_port = os.environ.get("PORT_SERVER")

ip_port = 80 if ip_port is None else ip_port
ip_server = "127.0.0.1" if ip_server is None else ip_server


@data_b.on_init
async def initialization(connect):
    # you can run your db initialization code here
    await connect.execute("SELECT 1")


@app.get(path='/access_token', tags=['Auth'], responses=access_token_res)
async def create_new_access_token(refresh_token: str, db=Depends(data_b.connection), ):
    """refresh_token: This is refresh token, use it for create new access token.
    You can get it when create account or login."""
    user_id = await conn.get_token(db=db, token_type='refresh', token=refresh_token)
    if not user_id:
        return JSONResponse(content={"ok": False,
                                     'description': "bad refresh token, please login"},
                            status_code=_status.HTTP_401_UNAUTHORIZED)
    await conn.delete_old_tokens(db=db)
    access = await conn.create_token(db=db, user_id=user_id[0][0], token_type='access')
    await conn.update_user_active(db=db, user_id=user_id[0][0])
    return {"ok": True,
            'user_id': user_id[0][0],
            'access_token': access[0][0]}


@app.get(path='/login', tags=['Auth'], responses=login_get_res)
async def login_user(email: str, auth_type: str, auth_id: int, access_token: str,
                           db=Depends(data_b.connection)):
    """Login user in service by fb"""
    user_data = await conn.read_data(db=db, name='*', table='all_users', id_name='email', id_data=email)
    if not user_data:
        return JSONResponse(content={"ok": True,
                                     'description': 'This email is not in database', },
                            status_code=_status.HTTP_200_OK,
                            headers={'content-type': 'application/json; charset=utf-8'})

    if auth_type == 'fb':
        if not await user_fb_check_auth(access_token, user_id=auth_id, email=email):
            return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                                content={"ok": False,
                                         'description': 'Bad auth_id or access_token', })
    else:
        return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                            content={"ok": False,
                                     'description': 'The selected auth type is not supported', })

    user = User(user_data[0])

    access = await conn.create_token(db=db, user_id=user.user_id, token_type='access')
    refresh = await conn.create_token(db=db, user_id=user.user_id, token_type='refresh')

    return JSONResponse(content={"ok": True,
                                 'user': user.get_user_json(),
                                 'access_token': access[0][0],
                                 'refresh_token': refresh[0][0]
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/user_email', tags=['Auth'], responses=get_me_res)
async def check_email(email: str, db=Depends(data_b.connection), ):
    """Here you can check your email.
    email: string email for check it in db"""

    user_data = await conn.read_data(db=db, name='*', table='all_users', id_name='email', id_data=email)
    if not user_data:
        return JSONResponse(content={"ok": True,
                                     'description': 'This email is not in database', },
                            status_code=_status.HTTP_200_OK,
                            headers={'content-type': 'application/json; charset=utf-8'})
    return JSONResponse(content={"ok": True,
                                 "auth_type": user_data[0]["auth_type"],
                                 'description': 'This email is in database',},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
