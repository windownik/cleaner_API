import os

import starlette.status as _status
from fastapi import Depends
from starlette.responses import Response, JSONResponse

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


@app.put(path='/user_status', tags=['Admin users'], responses=update_user_res)
async def update_user_information(user_id: int, status: str, access_token: str, db=Depends(data_b.connection)):
    """Admin Update user's status.

    user_id: users number from our service\n
    status: can be: worker, customer, admin, ban\n
    access_token: (Долгота) of home/work address\n"""

    if status != 'customer' and status != 'worker' and status != 'admin' and status != 'ban':
        return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                            content={"ok": False,
                                     'description': 'Bad users status', })

    admin_id = await conn.get_token_admin(db=db, token_type='access', token=access_token)
    if not admin_id:
        return JSONResponse(content={"ok": False,
                                     'description': "bad access token or not enough rights"},
                            status_code=_status.HTTP_401_UNAUTHORIZED)

    user_data = await conn.read_data(db=db, name='status', table='all_users', id_name='user_id',
                                     id_data=user_id)
    if user_data is None:
        return JSONResponse(content={"ok": False,
                                     'description': "I haven't user with this user_id."},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.update_data(db=db, name='status', id_name='user_id', id_data=user_id)

    return JSONResponse(content={"ok": True,
                                 'desc': 'users status updated'},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})
