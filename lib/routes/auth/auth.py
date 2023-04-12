import os

import starlette.status as _status
from fastapi import Depends
from starlette.responses import JSONResponse

from lib import sql_connect as conn
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


@app.get(path='/check_phone', tags=['Auth'], responses=check_phone_res)
async def find_phone_in_db(phone: int, db=Depends(data_b.connection)):
    """Check user in database"""
    user = await conn.read_data(db=db, name='id', table='all_users', id_name='phone', id_data=phone)
    if user:
        return JSONResponse(content={"ok": False,
                                     'description': "have user with same phone"},
                            status_code=_status.HTTP_226_IM_USED)
    return {"ok": True, 'desc': 'no phone in database'}
