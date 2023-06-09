import os

import starlette.status as _status
from fastapi import Depends
from starlette.responses import Response, JSONResponse

from lib import sql_connect as conn
from lib.check_access_fb import user_fb_check_auth, user_google_check_auth
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


@app.post(path='/user', tags=['User'], responses=create_user_res)
async def new_user(name: str, phone: int, email: str, auth_type: str, auth_id: int, description: str, lang: str,
                   city: str, street: str, house: str, latitudes: float, longitudes: float, status: str,
                   image_link: str, access_token: str, db=Depends(data_b.connection)):
    """Create new user in server.
    name: users name from Facebook or name of company\n
    phone: only numbers\n
    email: get from facebook API\n
    image_link: get from facebook API\n
    auth_type: at start version can be: fb, google, twit\n
    auth_id: users id in Facebook\n
    description: users account description\n
    status: can be customer and worker\n
    lang: users app Language can be: ru, en, heb\n\n
    Personal home/work address\n
    city: home/work city\n
    street: home/work street\n
    house: home/work house number can include / or letters\n
    latitudes: (Широта) of home/work address\n
    longitudes: (Долгота) of home/work address\n
    access_token: Facebook access token"""

    if status != 'customer' and status != 'worker':
        return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                            content={"ok": False,
                                     'description': 'Bad users status', })
    if lang != 'ru' and lang != 'en' and lang != 'heb':
        return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                            content={"ok": False,
                                     'description': 'Bad pick language', })

    user_data = {
        'user_id': 0,
        'name': name,
        'phone': phone,
        'email': email,
        'image_link': image_link,
        'auth_type': auth_type,
        'auth_id': auth_id,
        'description': description,
        'lang': lang,
        'city': city,
        'street': street,
        'house': house,
        'status': f'{status}_checking',
        'score': 5,
        'score_count': 0,
        'total_score': 0,
        'range': 500,
        'latitudes': float(latitudes),
        'longitudes': float(longitudes),
        'last_active': None,
        'create_date': None
    }
    if auth_type == 'fb':
        if not await user_fb_check_auth(access_token, user_id=auth_id, email=email):
            return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                                content={"ok": False,
                                         'description': 'Bad auth_id or access_token', })
    elif auth_type == 'google':
        if not user_google_check_auth(access_token=access_token, email=email):
            return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                                content={"ok": False,
                                         'description': 'Bad auth_id or access_token', })
    else:
        return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                            content={"ok": False,
                                     'description': 'The selected auth type is not supported', })

    user = User(data=user_data)
    await user.create_user(db=db)

    access = await conn.create_token(db=db, user_id=user.user_id, token_type='access')
    refresh = await conn.create_token(db=db, user_id=user.user_id, token_type='refresh')

    return JSONResponse(content={"ok": True,
                                 'user': user.get_user_json(),
                                 'access_token': access[0][0],
                                 'refresh_token': refresh[0][0]},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/user', tags=['User'], responses=get_me_res)
async def get_user_information(access_token: str, db=Depends(data_b.connection), ):
    """Here you can check your username and password. Get users information.
    access_token: This is access auth token. You can get it when create account, login or """
    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return Response(content="bad access token",
                        status_code=_status.HTTP_401_UNAUTHORIZED)
    user_data = await conn.read_data(db=db, name='*', table='all_users',
                                     id_name='user_id', id_data=user_id[0][0])
    if not user_data:
        return Response(content="no user in database",
                        status_code=_status.HTTP_401_UNAUTHORIZED)
    user = User(user_data[0])
    return JSONResponse(content={"ok": True,
                                 'user': user.get_user_json(),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/user', tags=['User'], responses=update_user_res)
async def update_user_information(name: str, phone: int, email: str, description: str, lang: str, city: str,
                                  street: str, house: str, latitudes: float, longitudes: float, status: str, range: int,
                                  access_token: str,
                                  db=Depends(data_b.connection)):
    """Update user's information.

    name: users name from Facebook or name of company\n
    phone: only numbers\n
    email: get from facebook API\n
    description: users account description\n
    status: can be customer and worker\n
    lang: users app Language can be: ru, en, heb\n\n
    range: search range in meters
    Personal home/work address\n
    city: home/work city\n
    street: home/work street\n
    house: home/work house number can include / or letters\n
    latitudes: (Широта) of home/work address\n
    longitudes: (Долгота) of home/work address\n"""

    if status != 'customer' and status != 'worker':
        return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                            content={"ok": False,
                                     'description': 'Bad users status', })
    if lang != 'ru' and lang != 'en' and lang != 'heb':
        return JSONResponse(status_code=_status.HTTP_400_BAD_REQUEST,
                            content={"ok": False,
                                     'description': 'Bad pick language', })

    user_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not user_id:
        return JSONResponse(content={"ok": False,
                                     'description': "bad access token"},
                            status_code=_status.HTTP_401_UNAUTHORIZED)

    user_status = await conn.read_data(db=db, name='status', table='all_users', id_name='user_id',
                                       id_data=user_id[0][0])
    if user_status:
        if status != user_status[0][0]:
            status = f'{status}_checking'

    await conn.update_user(db=db, name=name, phone=phone, email=email, description=description, lang=lang, city=city,
                           street=street, house=house, latitudes=latitudes, longitudes=longitudes,
                           status=status, range=range, user_id=user_id[0][0])
    return JSONResponse(content={"ok": True,
                                 'desc': 'all users information updated'},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/image_link', tags=['User'], responses=update_user_res)
async def update_image_link(image_link: str, access_token: str, db=Depends(data_b.connection)):
    """Update user's image_link.

    image_link: get from facebook API\n
    access_token: This is access auth token. You can get it when create account, login or\n
    """

    my_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not my_id:
        return JSONResponse(content={"ok": False, "description": "bad access token"},
                            status_code=_status.HTTP_401_UNAUTHORIZED)

    await conn.update_data(db=db, name='image_link', data=image_link, id_name='user_id', id_data=my_id[0][0],
                           table='all_users')
    return JSONResponse(content={"ok": True,
                                 'desc': 'all users information updated'},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/user_lang', tags=['User'], responses=update_user_res)
async def update_language(lang: str, access_token: str, db=Depends(data_b.connection)):
    """Update user's language.

    lang: can be ru, en, he\n
    access_token: This is access auth token. You can get it when create account, login or\n
    """

    my_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not my_id:
        return JSONResponse(content={"ok": False, "description": "bad access token"},
                            status_code=_status.HTTP_401_UNAUTHORIZED)

    if lang not in ('ru', 'en', 'he'):
        return JSONResponse(content={"ok": False, "description": "language cod not valid"},
                            status_code=_status.HTTP_400_BAD_REQUEST)

    await conn.update_data(db=db, name='lang', data=lang, id_name='user_id', id_data=my_id[0][0],
                           table='all_users')
    return JSONResponse(content={"ok": True,
                                 'desc': 'all users information updated'},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.put(path='/user_geo', tags=['User'], responses=update_user_res)
async def update_users_geo_position(latitude: float, longitude: float, access_token: str, db=Depends(data_b.connection)):
    """Update user's geo latitude and longitude.

    latitude: geo position latitude\n
    longitude: geo position longitude\n
    access_token: This is access auth token. You can get it when create account, login or\n
    """

    my_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not my_id:
        return JSONResponse(content={"ok": False, "description": "bad access token"},
                            status_code=_status.HTTP_401_UNAUTHORIZED)

    await conn.update_data(db=db, name='latitudes', data=latitude, id_name='user_id', id_data=my_id[0][0],
                           table='all_users')
    await conn.update_data(db=db, name='longitudes', data=longitude, id_name='user_id', id_data=my_id[0][0],
                           table='all_users')
    return JSONResponse(content={"ok": True,
                                 'desc': 'all users information updated'},
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})


@app.get(path='/get_user_by_id', tags=['User'], responses=get_me_res)
async def get_user_by_id(user_id: int, access_token: str, db=Depends(data_b.connection), ):
    """Return user with user_id.\n
    access_token: This is access auth token. You can get it when create account, login or """
    my_id = await conn.get_token(db=db, token_type='access', token=access_token)
    if not my_id:
        return JSONResponse(content={"ok": False, "description": "bad access token"},
                            status_code=_status.HTTP_401_UNAUTHORIZED)
    user_data = await conn.read_data(db=db, name='*', table='all_users',
                                     id_name='user_id', id_data=user_id)
    if not user_data:
        return JSONResponse(content={"ok": False, "description": "no user in database"},
                            status_code=_status.HTTP_400_BAD_REQUEST)
    user = User(user_data[0])
    return JSONResponse(content={"ok": True,
                                 'user': user.get_user_json(),
                                 },
                        status_code=_status.HTTP_200_OK,
                        headers={'content-type': 'application/json; charset=utf-8'})