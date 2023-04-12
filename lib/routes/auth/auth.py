import os

from hashlib import sha256
import starlette.status as _status
from fastapi import Depends
from starlette.responses import Response, JSONResponse

from lib import sql_connect as conn
from lib.check_password import check_password, check_new_user_data
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


@app.get(path='/create_db', tags=['System'], )
async def init_database(db=Depends(data_b.connection)):
    """Here you can check your username and password"""
    await conn.create_all_users_table(db)
    await conn.create_token_table(db)
    return {"ok": True}


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


@app.get(path='/login', tags=['Auth'], responses=login_res)
async def find_phone_in_db(phone: int, password: str, db=Depends(data_b.connection)):
    """Check user in database"""
    user = await conn.read_data(db=db, name='id, password_hash', table='all_users', id_name='phone', id_data=phone)
    if not user:
        return JSONResponse(content={"ok": False,
                                     'description': "no user in database"},
                            status_code=_status.HTTP_226_IM_USED)
    pass_hash = sha256(password.encode('utf-8')).hexdigest()
    if pass_hash != user[0][1]:
        return JSONResponse(content={"ok": False,
                                     'description': "bad phone or password"},
                            status_code=_status.HTTP_401_UNAUTHORIZED)
    user_id = user[0][0]
    access = await conn.create_token(db=db, user_id=user_id, token_type='access')
    refresh = await conn.create_token(db=db, user_id=user_id, token_type='refresh')
    return {"ok": True,
            'user_id': user_id,
            'access_token': access[0][0],
            'refresh_token': refresh[0][0]}


@app.put(path='/change_password', tags=['Auth'], responses=update_pass_res)
async def find_phone_in_db(phone: int, password: str, new_password: str, db=Depends(data_b.connection)):
    """Check user in database"""
    user = await conn.read_data(db=db, name='id, password_hash', table='all_users', id_name='phone', id_data=phone)
    if not user:
        return Response(content="no user in database",
                        status_code=_status.HTTP_226_IM_USED)
    pass_hash = sha256(password.encode('utf-8')).hexdigest()
    if pass_hash != user[0][1]:
        return Response(content="bad phone or password",
                        status_code=_status.HTTP_401_UNAUTHORIZED)
    if len(new_password) < 6:
        return Response(content="min password length is 6",
                        status_code=_status.HTTP_226_IM_USED)
    if not check_password(password=new_password):
        return Response(content="bad letters in password",
                        status_code=_status.HTTP_226_IM_USED)
    pass_hash = sha256(new_password.encode('utf-8')).hexdigest()
    user_id = user[0][0]
    await conn.update_password(db=db, user_id=user_id, password_hash=pass_hash)
    await conn.delete_all_tokens(db=db, user_id=user_id)
    access = await conn.create_token(db=db, user_id=user_id, token_type='access')
    refresh = await conn.create_token(db=db, user_id=user_id, token_type='refresh')
    return {"ok": True,
            'user_id': user_id,
            'access_token': access[0][0],
            'refresh_token': refresh[0][0]}


@app.post(path='/user', tags=['User'], responses=create_user_res)
async def new_user(name: str, surname: str, phone: int, email: str, password: str, status: str,
                   db=Depends(data_b.connection)):
    """Create new user in auth server, email is optional. If there is no email then send 0.

    status can be: simple, creator, admin"""
    check = await check_new_user_data(password=password, status=status, conn=conn, db=db, phone=phone)
    if check != 'good':
        return check

    pass_hash = sha256(password.encode('utf-8')).hexdigest()
    user_id = \
        (await conn.create_user(db=db, phone=phone, email=email, status=status, password_hash=pass_hash, name=name,
                                surname=surname))[0][0]
    access = await conn.create_token(db=db, user_id=user_id, token_type='access')
    refresh = await conn.create_token(db=db, user_id=user_id, token_type='refresh')
    return {"ok": True,
            'user_id': user_id,
            'access_token': access[0][0],
            'refresh_token': refresh[0][0]}


@app.get(path='/user', tags=['User'], responses=get_me_res)
async def get_user_information(access_token: str, db=Depends(data_b.connection), ):
    """Here you can check your username and password. Get users information.
    access_token: This is access auth token. You can get it when create account, login or """
    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)
    user = await conn.read_data(db=db, name='phone, email, name, surname, status, last_active', table='all_users',
                                id_name='id', id_data=user_id[0][0])
    if not user:
        return Response(content="no user in database",
                        status_code=_status.HTTP_401_UNAUTHORIZED)
    return {"ok": True,
            'user_id': user_id[0][0],
            'name': user[0]['name'],
            'surname': user[0]['surname'],
            'phone': user[0]['phone'],
            'email': user[0]['email'],
            'status': user[0]['status'],
            'last_active': user[0]['last_active'],
            }


@app.put(path='/user', tags=['User'], responses=update_user_res)
async def update_user_information(name: str, surname: str, email: str, access_token: str, status: str,
                                  db=Depends(data_b.connection)):
    """Update new user in auth server, email is optional. If there is no email then send 0.

    status can be: simple, creator, admin"""
    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)

    await conn.update_user(db=db, email=email, status=status, name=name, surname=surname, user_id=user_id[0][0])
    return {"ok": True,
            'desc': 'all users information updated'}
